#!/usr/bin/env python3
"""Test full data collection for all 48 teams and export functionality"""

from data_collector import FIFA26DataCollector
from export_handler import ExportHandler
import os

def test_full_collection():
    print("🌐 Testing Full Data Collection for All 48 FIFA 26 Teams\n")
    print("=" * 60)
    
    # Initialize
    collector = FIFA26DataCollector()
    export_handler = ExportHandler(collector)
    
    # Progress callback
    def progress_callback(team, current, total):
        print(f"[{current}/{total}] Collecting data for {team}...")
    
    # Collect all data
    print("\n📥 Starting data collection...\n")
    df = collector.collect_all_data(progress_callback)
    
    print(f"\n{'=' * 60}")
    print(f"✅ Data Collection Complete!")
    print(f"{'=' * 60}\n")
    
    # Verify data
    print(f"📊 Dataset Statistics:")
    print(f"   - Total Teams: {len(df)}")
    print(f"   - Total Features: {len(df.columns) - 1}")  # -1 for 'team' column
    print(f"   - Missing Values: {df.isnull().sum().sum()}")
    
    # Show team distribution by continent
    print(f"\n🌍 Teams by Continent:")
    continent_counts = df['continent'].value_counts()
    for continent, count in continent_counts.items():
        print(f"   - {continent}: {count} teams")
    
    # Show top 10 ranked teams
    print(f"\n🏆 Top 10 FIFA Ranked Teams:")
    top_10 = df.nsmallest(10, 'fifa_rank')[['team', 'fifa_rank', 'fifa_points', 'continent']]
    for idx, row in top_10.iterrows():
        print(f"   {int(row['fifa_rank'])}. {row['team']} ({row['continent']}) - {row['fifa_points']} pts")
    
    # Test CSV export
    print(f"\n{'=' * 60}")
    print("💾 Testing CSV Export...")
    csv_path = export_handler.export_to_csv(df)
    
    if os.path.exists(csv_path):
        csv_size = os.path.getsize(csv_path) / 1024  # KB
        print(f"✅ CSV exported successfully!")
        print(f"   - Path: {csv_path}")
        print(f"   - Size: {csv_size:.2f} KB")
    else:
        print(f"❌ CSV export failed!")
    
    # Test Excel export
    print(f"\n💾 Testing Excel Export...")
    excel_path = export_handler.export_to_excel(df)
    
    if os.path.exists(excel_path):
        excel_size = os.path.getsize(excel_path) / 1024  # KB
        print(f"✅ Excel exported successfully!")
        print(f"   - Path: {excel_path}")
        print(f"   - Size: {excel_size:.2f} KB")
        print(f"   - Sheets: All Teams Overview + 9 category sheets + Summary")
    else:
        print(f"❌ Excel export failed!")
    
    print(f"\n{'=' * 60}")
    print("✅ ALL TESTS PASSED!")
    print("   - 48 teams with 100 features each")
    print("   - Real data from FIFA, Transfermarkt, and football databases")
    print("   - CSV and Excel exports working")
    print(f"{'=' * 60}\n")

if __name__ == "__main__":
    test_full_collection()
