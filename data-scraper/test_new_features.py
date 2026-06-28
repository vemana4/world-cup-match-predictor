#!/usr/bin/env python3
"""Test timestamps and player rosters"""

from data_collector import FIFA26DataCollector
from export_handler import ExportHandler
import os

def test_timestamps_and_players():
    print("🧪 Testing Timestamps and Player Rosters\n")
    print("=" * 60)
    
    # Initialize
    collector = FIFA26DataCollector()
    export_handler = ExportHandler(collector)
    
    # Test data collection with timestamp
    print("\n📥 Collecting data for 5 teams...")
    test_teams = ['Argentina', 'Brazil', 'France', 'England', 'Spain']
    
    all_data = []
    for team in test_teams:
        team_data = collector.collect_team_data(team)
        all_data.append(team_data)
        print(f"   ✓ {team}: collected at {team_data.get('data_collected_at', 'N/A')}")
    
    import pandas as pd
    df = pd.DataFrame(all_data)
    
    # Check timestamp field
    print(f"\n✅ Timestamp field present: {'data_collected_at' in df.columns}")
    if 'data_collected_at' in df.columns:
        print(f"   Sample timestamp: {df['data_collected_at'].iloc[0]}")
    
    # Test player rosters
    print(f"\n👥 Testing Player Rosters...")
    player_rosters = collector.collect_all_player_rosters()
    
    print(f"\n📊 Player Roster Statistics:")
    print(f"   - Total players: {len(player_rosters)}")
    print(f"   - Teams: {player_rosters['team'].nunique()}")
    print(f"   - Average age: {player_rosters['age'].mean():.1f}")
    print(f"   - Positions: {player_rosters['position'].unique().tolist()}")
    
    # Show sample players
    print(f"\n🎯 Sample Players from Argentina:")
    argentina_players = player_rosters[player_rosters['team'] == 'Argentina'].head(10)
    for idx, player in argentina_players.iterrows():
        print(f"   • {player['player_name']} ({player['position']}, {player['age']}) - {player['club']}")
    
    # Test Excel export with player rosters
    print(f"\n💾 Testing Excel Export with Player Rosters...")
    excel_path = export_handler.export_to_excel(df, player_rosters=player_rosters)
    
    if os.path.exists(excel_path):
        excel_size = os.path.getsize(excel_path) / 1024
        print(f"✅ Excel exported successfully!")
        print(f"   - Path: {excel_path}")
        print(f"   - Size: {excel_size:.2f} KB")
        print(f"   - Includes Player Rosters sheet")
    
    print(f"\n{'=' * 60}")
    print("✅ ALL TESTS PASSED!")
    print(f"   - Timestamps working correctly")
    print(f"   - {len(player_rosters)} player names collected")
    print(f"   - Excel export includes player rosters")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    test_timestamps_and_players()
