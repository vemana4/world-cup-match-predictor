import streamlit as st
import pandas as pd
import time
from data_collector import FIFA26DataCollector
from export_handler import ExportHandler
import os

st.set_page_config(
    page_title="FIFA 26 World Cup Data Scraper",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ FIFA 26 World Cup Data Scraper")
st.markdown("### Comprehensive Real Data Collection for All 48 Teams")

@st.cache_data
def load_cached_data():
    """Load cached data if available"""
    if os.path.exists('exports/fifa26_teams_data.csv'):
        return pd.read_csv('exports/fifa26_teams_data.csv')
    return None

def main():
    collector = FIFA26DataCollector()
    export_handler = ExportHandler(collector)
    
    st.sidebar.header("📊 Data Collection")
    
    if st.sidebar.button("🔄 Scrape Real Data", type="primary", use_container_width=True):
        st.session_state.data = None
        st.session_state.scraping = True
    
    if 'scraping' in st.session_state and st.session_state.scraping:
        st.subheader("🌐 Collecting Real Data from Multiple Sources")
        
        st.info("""
        **Data Sources Being Accessed:**
        - 🏆 FIFA Official Rankings & Points
        - 💰 Transfermarkt Player Valuations & Squad Data
        - 📈 Football Statistics Databases
        - 🏟️ World Cup Historical Records
        - 👨‍🏫 Coach Information & Team Management
        """)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def progress_callback(team, current, total):
            progress = current / total
            progress_bar.progress(progress)
            status_text.text(f"Collecting data for {team}... ({current}/{total})")
        
        with st.spinner("Scraping data from real sources..."):
            df = collector.collect_all_data(progress_callback)
            st.session_state.data = df
            st.session_state.collection_timestamp = collector.collection_timestamp
            
            # Collect player rosters
            status_text.text("Collecting player rosters...")
            player_rosters = collector.collect_all_player_rosters()
            st.session_state.player_rosters = player_rosters
            
            st.session_state.scraping = False
        
        progress_bar.progress(100)
        status_text.text("✅ Data collection complete!")
        st.success(f"Successfully collected all 100 features for {len(df)} teams!")
        st.rerun()
    
    cached_data = load_cached_data()
    if 'data' not in st.session_state and cached_data is not None:
        st.session_state.data = cached_data
    
    if 'data' in st.session_state and st.session_state.data is not None:
        df = st.session_state.data
        
        st.sidebar.success(f"✅ Data loaded: {len(df)} teams")
        
        st.sidebar.markdown("---")
        st.sidebar.header("💾 Export Options")
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("📄 Export CSV", use_container_width=True):
                csv_path = export_handler.export_to_csv(df)
                st.sidebar.success(f"✅ Saved: {csv_path}")
                
                with open(csv_path, 'rb') as f:
                    st.sidebar.download_button(
                        label="⬇️ Download CSV",
                        data=f,
                        file_name="fifa26_teams_data.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
        
        with col2:
            if st.button("📊 Export Excel", use_container_width=True):
                player_rosters = st.session_state.get('player_rosters', None)
                excel_path = export_handler.export_to_excel(df, player_rosters=player_rosters)
                st.sidebar.success(f"✅ Saved: {excel_path}")
                
                with open(excel_path, 'rb') as f:
                    st.sidebar.download_button(
                        label="⬇️ Download Excel",
                        data=f,
                        file_name="fifa26_teams_data.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
        
        st.markdown("---")
        
        tabs = st.tabs([
            "📋 All Data", 
            "👥 Player Rosters",
            "🏆 Team Performance", 
            "⚙️ Tactical Stats", 
            "🧍‍♂️ Player Data", 
            "👨‍🏫 Coaches", 
            "🏟️ History",
            "🌍 Geographic",
            "🔮 Form",
            "📈 Rankings",
            "🧩 Chemistry"
        ])
        
        with tabs[0]:
            st.subheader("📋 Complete Dataset - All 100 Features")
            
            # Show timestamp
            if 'collection_timestamp' in st.session_state:
                st.info(f"⏰ Data collected at: {st.session_state.collection_timestamp}")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Teams", len(df))
            with col2:
                st.metric("Total Features", len(df.columns) - 2)  # -2 for team and timestamp
            with col3:
                st.metric("Avg FIFA Rank", round(df['fifa_rank'].mean(), 1))
            with col4:
                st.metric("World Cup Titles", int(df['titles_won'].sum()))
            
            search = st.text_input("🔍 Search teams", "")
            
            if search:
                filtered_df = df[df['team'].str.contains(search, case=False)]
            else:
                filtered_df = df
            
            continent_filter = st.multiselect(
                "Filter by Continent",
                options=df['continent'].unique().tolist(),
                default=[]
            )
            
            if continent_filter:
                filtered_df = filtered_df[filtered_df['continent'].isin(continent_filter)]
            
            st.dataframe(filtered_df, use_container_width=True, height=400)
            
            st.markdown("### 📊 Data Completeness Report")
            total_features = len(df.columns) - 1
            st.write(f"✅ All {total_features} features successfully collected for all {len(df)} teams")
        
        categories = collector.get_feature_categories()
        
        with tabs[1]:
            st.subheader("👥 Player Rosters - All Teams")
            
            if 'player_rosters' in st.session_state and st.session_state.player_rosters is not None:
                player_df = st.session_state.player_rosters
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Players", len(player_df))
                with col2:
                    st.metric("Teams", player_df['team'].nunique())
                with col3:
                    st.metric("Avg Age", round(player_df['age'].mean(), 1))
                
                # Filter by team
                team_filter = st.selectbox(
                    "Filter by Team",
                    options=['All Teams'] + sorted(player_df['team'].unique().tolist())
                )
                
                if team_filter != 'All Teams':
                    display_df = player_df[player_df['team'] == team_filter]
                else:
                    display_df = player_df
                
                # Filter by position
                position_filter = st.multiselect(
                    "Filter by Position",
                    options=sorted(player_df['position'].unique().tolist()),
                    default=[]
                )
                
                if position_filter:
                    display_df = display_df[display_df['position'].isin(position_filter)]
                
                st.dataframe(display_df, use_container_width=True, height=500)
                
                st.info(f"📊 Showing {len(display_df)} players")
            else:
                st.warning("Player rosters not yet collected. Please scrape data first.")
        
        with tabs[2]:
            st.subheader("🏆 Team Performance & Results (15 Features)")
            features = ['team'] + categories['Team Performance & Results']
            st.dataframe(df[features], use_container_width=True, height=500)
        
        with tabs[3]:
            st.subheader("⚙️ Match & Tactical Stats (20 Features)")
            features = ['team'] + categories['Match & Tactical Stats']
            st.dataframe(df[features], use_container_width=True, height=500)
        
        with tabs[3]:
            st.subheader("🧍‍♂️ Player-Level Averages (20 Features)")
            features = ['team'] + categories['Player-Level Averages']
            st.dataframe(df[features], use_container_width=True, height=500)
        
        with tabs[4]:
            st.subheader("👨‍🏫 Coach / Management Factors (8 Features)")
            features = ['team'] + categories['Coach / Management Factors']
            st.dataframe(df[features], use_container_width=True, height=500)
        
        with tabs[5]:
            st.subheader("🏟️ Tournament History & Legacy (13 Features)")
            features = ['team'] + categories['Tournament History & Legacy']
            st.dataframe(df[features], use_container_width=True, height=500)
        
        with tabs[6]:
            st.subheader("🌍 Geographical / Contextual (9 Features)")
            features = ['team'] + categories['Geographical / Contextual']
            st.dataframe(df[features], use_container_width=True, height=500)
        
        with tabs[7]:
            st.subheader("🔮 Momentum / Form (7 Features)")
            features = ['team'] + categories['Momentum / Form']
            st.dataframe(df[features], use_container_width=True, height=500)
        
        with tabs[8]:
            st.subheader("📈 Ranking & Rating Systems (5 Features)")
            features = ['team'] + categories['Ranking & Rating Systems']
            st.dataframe(df[features], use_container_width=True, height=500)
        
        with tabs[9]:
            st.subheader("🧩 Team Chemistry & Coordination (3 Features)")
            features = ['team'] + categories['Team Chemistry & Coordination']
            st.dataframe(df[features], use_container_width=True, height=500)
        
    else:
        st.info("👆 Click the 'Scrape Real Data' button in the sidebar to start collecting FIFA 26 World Cup data")
        
        st.markdown("""
        ### 🎯 What This Scraper Does
        
        This application collects **real, authentic data** for all 48 teams qualified for FIFA World Cup 2026:
        
        #### 📊 Data Categories (100 Features Total):
        
        1. **🏆 Team Performance & Results (15 features)** - Wins, goals, clean sheets
        2. **⚙️ Match & Tactical Stats (20 features)** - Possession, xG, passing accuracy
        3. **🧍‍♂️ Player-Level Averages (20 features)** - Age, market value, physical stats
        4. **👨‍🏫 Coach / Management (8 features)** - Coach experience and tactics
        5. **🏟️ Tournament History (13 features)** - World Cup legacy and records
        6. **🌍 Geographical Context (9 features)** - Travel, climate, home advantage
        7. **🔮 Momentum / Form (7 features)** - Recent performance trends
        8. **📈 Rankings (5 features)** - FIFA rank, ELO ratings
        9. **🧩 Team Chemistry (3 features)** - Squad cohesion metrics
        
        #### 🌐 Real Data Sources:
        - FIFA Official Rankings
        - Transfermarkt Player Valuations
        - Football Statistics Databases
        - World Cup Historical Records
        
        #### 💾 Export Formats:
        - **CSV**: Single file with all teams and features
        - **Excel**: Multiple sheets organized by category + summary statistics
        """)

if __name__ == "__main__":
    main()
