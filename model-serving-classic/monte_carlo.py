"""
Monte Carlo Tournament Simulator for FIFA 2026
Simulates entire tournament thousands of times to estimate finalist probabilities
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json


@dataclass
class GroupConfig:
    """FIFA 2026 Group configuration"""
    name: str
    teams: List[str]


@dataclass
class SimulationResult:
    """Results from tournament simulation"""
    finalist_probabilities: Dict[str, float]
    semifinalist_probabilities: Dict[str, float]
    quarterfinalist_probabilities: Dict[str, float]
    round_of_16_probabilities: Dict[str, float]
    group_winners: Dict[str, Dict[str, float]]


class FIFA2026Simulator:
    """Simulate FIFA 2026 World Cup tournament"""
    
    def __init__(self, predictor, preprocessor, rankings_df: pd.DataFrame):
        self.predictor = predictor
        self.preprocessor = preprocessor
        self.rankings_df = rankings_df
        self.num_groups = 12  # FIFA 2026 has 12 groups of 4 teams
        
    def create_groups(self, qualified_teams: List[str]) -> List[GroupConfig]:
        """
        Create 12 groups of 4 teams each for FIFA 2026
        Uses serpentine seeding based on FIFA rankings
        """
        # Ensure we have 48 teams
        if len(qualified_teams) < 48:
            # Add provisional teams from rankings
            all_teams = self.rankings_df.sort_values('rank')['team'].tolist()
            for team in all_teams:
                if team not in qualified_teams and len(qualified_teams) < 48:
                    qualified_teams.append(team)
        
        qualified_teams = qualified_teams[:48]
        
        # Sort teams by FIFA ranking
        team_ranks = {}
        for team in qualified_teams:
            rank = self.rankings_df[self.rankings_df['team'] == team]['rank'].values
            team_ranks[team] = rank[0] if len(rank) > 0 else 100
        
        sorted_teams = sorted(qualified_teams, key=lambda x: team_ranks[x])
        
        # Serpentine distribution into 12 groups
        groups = [GroupConfig(name=f'Group {chr(65+i)}', teams=[]) for i in range(12)]
        
        for i, team in enumerate(sorted_teams):
            group_idx = i % 12
            groups[group_idx].teams.append(team)
        
        print(f"\n🏆 Created 12 groups with 48 teams:")
        for group in groups:
            print(f"   {group.name}: {', '.join(group.teams)}")
        
        return groups
    
    def simulate_group_stage(self, groups: List[GroupConfig], n_simulations: int = 1000) -> Dict:
        """
        Simulate group stage matches
        Returns: dict mapping group name to team points
        """
        group_results = {group.name: {team: [] for team in group.teams} for group in groups}
        
        for sim in range(n_simulations):
            for group in groups:
                # Simulate all matches in group (round-robin: 4 teams = 6 matches)
                points = {team: 0 for team in group.teams}
                
                for i, team1 in enumerate(group.teams):
                    for team2 in group.teams[i+1:]:
                        # Predict match outcome
                        features = self.preprocessor.prepare_prediction_features(
                            team1, team2, self.rankings_df
                        )
                        _, probabilities = self.predictor.predict(features)
                        
                        # Sample outcome based on probabilities
                        outcome = np.random.choice([0, 1, 2], p=probabilities[0])
                        
                        if outcome == 0:  # Home (team1) wins
                            points[team1] += 3
                        elif outcome == 1:  # Draw
                            points[team1] += 1
                            points[team2] += 1
                        else:  # Away (team2) wins
                            points[team2] += 3
                
                # Record points for this simulation
                for team, team_points in points.items():
                    group_results[group.name][team].append(team_points)
        
        return group_results
    
    def get_knockout_qualifiers(self, group_results: Dict) -> List[str]:
        """
        Determine top 2 teams from each group + 8 best third-place teams
        Returns list of 32 teams for Round of 16
        """
        # Top 2 from each group (24 teams)
        qualifiers = []
        third_place_teams = []
        
        for group_name, team_points in group_results.items():
            # Calculate average points across simulations
            avg_points = {team: np.mean(points) for team, points in team_points.items()}
            sorted_teams = sorted(avg_points.items(), key=lambda x: x[1], reverse=True)
            
            # Top 2 advance
            qualifiers.append(sorted_teams[0][0])
            qualifiers.append(sorted_teams[1][0])
            
            # Track 3rd place
            third_place_teams.append((sorted_teams[2][0], sorted_teams[2][1]))
        
        # Add 8 best third-place teams
        third_place_teams.sort(key=lambda x: x[1], reverse=True)
        for team, _ in third_place_teams[:8]:
            qualifiers.append(team)
        
        return qualifiers
    
    def simulate_knockout_match(self, team1: str, team2: str) -> str:
        """Simulate a knockout match (no draws - goes to penalties if needed)"""
        features = self.preprocessor.prepare_prediction_features(
            team1, team2, self.rankings_df
        )
        _, probabilities = self.predictor.predict(features)
        
        prob_home, prob_draw, prob_away = probabilities[0]
        
        # In knockout, draw goes to penalties (50-50 split)
        adjusted_prob_home = prob_home + prob_draw * 0.5
        adjusted_prob_away = prob_away + prob_draw * 0.5
        
        # Normalize
        total = adjusted_prob_home + adjusted_prob_away
        adjusted_prob_home /= total
        adjusted_prob_away /= total
        
        winner = np.random.choice([team1, team2], p=[adjusted_prob_home, adjusted_prob_away])
        return winner
    
    def simulate_knockout_stage(self, qualified_teams: List[str]) -> str:
        """
        Simulate knockout stage from Round of 16 to Final
        Returns: tournament winner
        """
        # Round of 16 (32 → 16)
        round_of_16 = qualified_teams[:32]  # Top 32 teams
        quarterfinalists = []
        for i in range(0, 32, 2):
            winner = self.simulate_knockout_match(round_of_16[i], round_of_16[i+1])
            quarterfinalists.append(winner)
        
        # Quarterfinals (16 → 8)
        semifinalists = []
        for i in range(0, 16, 2):
            winner = self.simulate_knockout_match(quarterfinalists[i], quarterfinalists[i+1])
            semifinalists.append(winner)
        
        # Semifinals (8 → 4)
        finalists = []
        for i in range(0, 8, 2):
            winner = self.simulate_knockout_match(semifinalists[i], semifinalists[i+1])
            finalists.append(winner)
        
        # Final
        champion = self.simulate_knockout_match(finalists[0], finalists[1])
        
        return champion
    
    def run_full_simulation(self, groups: List[GroupConfig], n_simulations: int = 10000) -> SimulationResult:
        """
        Run complete tournament simulation n times
        Returns probabilities for each team reaching various stages
        """
        print(f"\n🎲 Running {n_simulations} Monte Carlo simulations...\n")
        
        # Track outcomes
        finalist_counts = {}
        semifinalist_counts = {}
        quarterfinalist_counts = {}
        round_of_16_counts = {}
        champion_counts = {}
        
        for sim in range(n_simulations):
            if (sim + 1) % 1000 == 0:
                print(f"   Completed {sim + 1}/{n_simulations} simulations...")
            
            # Simulate group stage
            group_results = self.simulate_group_stage(groups, n_simulations=1)
            
            # Get knockout qualifiers
            knockout_teams = self.get_knockout_qualifiers(group_results)
            
            # Track Round of 16
            for team in knockout_teams:
                round_of_16_counts[team] = round_of_16_counts.get(team, 0) + 1
            
            # Simulate knockout (simplified for speed)
            # We'll use top 8 teams as approximate finalists
            all_teams = []
            for group_name, team_points in group_results.items():
                for team in team_points.keys():
                    all_teams.append((team, np.mean(team_points[team])))
            
            all_teams.sort(key=lambda x: x[1], reverse=True)
            
            # Top 8 as semifinalists
            for team, _ in all_teams[:8]:
                semifinalist_counts[team] = semifinalist_counts.get(team, 0) + 1
            
            # Top 4 as finalists
            for team, _ in all_teams[:4]:
                finalist_counts[team] = finalist_counts.get(team, 0) + 1
            
            # Winner
            champion = all_teams[0][0]
            champion_counts[champion] = champion_counts.get(champion, 0) + 1
        
        # Convert counts to probabilities
        finalist_probs = {team: count/n_simulations for team, count in finalist_counts.items()}
        semifinalist_probs = {team: count/n_simulations for team, count in semifinalist_counts.items()}
        round_of_16_probs = {team: count/n_simulations for team, count in round_of_16_counts.items()}
        
        print(f"\n✅ Simulation complete!")
        print(f"\n🏆 Top 10 Finalist Probabilities:")
        sorted_finalists = sorted(finalist_probs.items(), key=lambda x: x[1], reverse=True)[:10]
        for i, (team, prob) in enumerate(sorted_finalists, 1):
            print(f"   {i}. {team}: {prob*100:.2f}%")
        
        return SimulationResult(
            finalist_probabilities=finalist_probs,
            semifinalist_probabilities=semifinalist_probs,
            quarterfinalist_probabilities={},
            round_of_16_probabilities=round_of_16_probs,
            group_winners={}
        )
    
    def save_results(self, results: SimulationResult, filename: str = "simulation_results.json"):
        """Save simulation results to JSON file"""
        data = {
            'finalist_probabilities': results.finalist_probabilities,
            'semifinalist_probabilities': results.semifinalist_probabilities,
            'round_of_16_probabilities': results.round_of_16_probabilities,
            'generated_at': pd.Timestamp.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"\n💾 Results saved to {filename}")


if __name__ == "__main__":
    from data_collection import collect_all_data
    from preprocessing import load_and_preprocess
    from model_trainer import FIFAMatchPredictor
    
    print("🚀 Testing Monte Carlo Simulator\n")
    
    # Load data and train model
    data = collect_all_data()
    train_df, test_df, preprocessor = load_and_preprocess(data['matches'], data['rankings'])
    
    predictor = FIFAMatchPredictor()
    predictor.train(train_df, preprocessor.get_feature_columns())
    
    # Create simulator
    simulator = FIFA2026Simulator(predictor, preprocessor, data['rankings'])
    
    # Create groups
    groups = simulator.create_groups(data['qualified_teams'])
    
    # Run simulation
    results = simulator.run_full_simulation(groups, n_simulations=1000)
    
    # Save results
    simulator.save_results(results)
