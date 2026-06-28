#!/usr/bin/env python3
"""Verify that all 100 features are properly collected"""

from data_collector import FIFA26DataCollector
import pandas as pd

def verify_all_features():
    print("🔍 Verifying FIFA 26 Data Scraper - All 100 Features\n")
    print("=" * 60)
    
    # Initialize collector
    collector = FIFA26DataCollector()
    
    # Get expected feature categories
    categories = collector.get_feature_categories()
    
    print("\n📋 Expected Feature Categories:")
    total_expected = 0
    for category, features in categories.items():
        print(f"\n{category}: {len(features)} features")
        total_expected += len(features)
    
    print(f"\n{'=' * 60}")
    print(f"Total Expected Features: {total_expected}")
    print(f"{'=' * 60}\n")
    
    # Collect data for one test team
    print("🌐 Testing data collection for Argentina...\n")
    test_team_data = collector.collect_team_data('Argentina')
    
    # Count actual features collected (excluding 'team' field)
    actual_features = len(test_team_data) - 1  # -1 for 'team' field
    
    print(f"✅ Collected {actual_features} features for Argentina\n")
    
    # Verify all expected features are present
    print("🔎 Verifying each category:\n")
    
    all_features_present = True
    for category, features in categories.items():
        missing = []
        for feature in features:
            if feature not in test_team_data:
                missing.append(feature)
                all_features_present = False
        
        if missing:
            print(f"❌ {category}: MISSING {len(missing)} features")
            for m in missing:
                print(f"   - {m}")
        else:
            print(f"✅ {category}: All {len(features)} features present")
    
    print(f"\n{'=' * 60}")
    
    if all_features_present and actual_features == total_expected:
        print(f"✅ SUCCESS! All {total_expected} features are properly implemented!")
        print(f"{'=' * 60}\n")
        
        # Show sample of collected data
        print("📊 Sample Data for Argentina:\n")
        sample_features = [
            'team', 'fifa_rank', 'fifa_points', 'total_wins', 'total_losses',
            'goals_scored_total', 'avg_player_age', 'total_squad_value',
            'coach_name', 'titles_won', 'continent', 'elo_rating'
        ]
        
        for feature in sample_features:
            if feature in test_team_data:
                print(f"{feature}: {test_team_data[feature]}")
        
        return True
    else:
        print(f"❌ FAILED! Expected {total_expected} features but got {actual_features}")
        print(f"{'=' * 60}\n")
        return False

if __name__ == "__main__":
    success = verify_all_features()
    exit(0 if success else 1)
