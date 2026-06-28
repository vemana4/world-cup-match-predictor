import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import pandas as pd

st.set_page_config(
    page_title="FIFA 2026 World Cup Prediction System v3.0",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_BASE_URL = "http://localhost:8000/api"

st.title("⚽ FIFA 2026 World Cup Prediction System v3.0")
st.markdown("*State-of-the-Art AI with 80%+ Target Accuracy | Dual-Regression Goal Prediction*")

st.markdown("---")

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🎯 Match Prediction",
    "🏆 Tournament Simulation",
    "📊 Match Context",
    "🚨 Injury Alerts",
    "📈 Model Explainability"
])

with tab1:
    st.header("Match Outcome Prediction")
    st.markdown("**Using Dual-Regression Goal Prediction Model**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        home_team = st.text_input("Home Team", value="France", key="home_team")
        competition = st.selectbox("Competition", [
            "FIFA World Cup", "FIFA World Cup Qualifier",
            "UEFA Nations League", "Copa America", "Friendly"
        ], key="competition")
    
    with col2:
        away_team = st.text_input("Away Team", value="Brazil", key="away_team")
        venue = st.text_input("Venue (Optional)", value="", key="venue")
    
    if st.button("🔮 Get Prediction", type="primary", use_container_width=True):
        with st.spinner("Running dual-regression goal prediction model..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/predict",
                    json={
                        "home_team_name": home_team,
                        "away_team_name": away_team,
                        "competition": competition,
                        "venue": venue if venue else None
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    prediction = response.json()
                    
                    st.success("✅ Prediction Generated Successfully!")
                    
                    col_a, col_b, col_c = st.columns(3)
                    
                    with col_a:
                        st.metric(
                            "Most Likely Score",
                            prediction['most_likely_score'],
                            help="Based on Poisson goal distributions"
                        )
                    
                    with col_b:
                        st.metric(
                            "Home Win Probability",
                            f"{prediction['home_win_prob'] * 100:.1f}%"
                        )
                    
                    with col_c:
                        st.metric(
                            "Confidence Score",
                            f"{prediction['confidence_score'] * 100:.1f}%"
                        )
                    
                    st.markdown("---")
                    
                    col_pred1, col_pred2 = st.columns(2)
                    
                    with col_pred1:
                        st.subheader("Predicted Goals")
                        fig_goals = go.Figure(data=[
                            go.Bar(
                                x=[home_team, away_team],
                                y=[prediction['predicted_home_goals'], prediction['predicted_away_goals']],
                                marker_color=['#3498db', '#e74c3c'],
                                text=[f"{prediction['predicted_home_goals']:.2f}", f"{prediction['predicted_away_goals']:.2f}"],
                                textposition='auto'
                            )
                        ])
                        fig_goals.update_layout(
                            title="Expected Goals (xG)",
                            yaxis_title="Goals",
                            showlegend=False,
                            height=300
                        )
                        st.plotly_chart(fig_goals, use_container_width=True)
                    
                    with col_pred2:
                        st.subheader("Win/Draw/Loss Probabilities")
                        fig_probs = go.Figure(data=[
                            go.Pie(
                                labels=[f'{home_team} Win', 'Draw', f'{away_team} Win'],
                                values=[
                                    prediction['home_win_prob'],
                                    prediction['draw_prob'],
                                    prediction['away_win_prob']
                                ],
                                marker_colors=['#3498db', '#95a5a6', '#e74c3c'],
                                hole=0.4
                            )
                        ])
                        fig_probs.update_layout(height=300)
                        st.plotly_chart(fig_probs, use_container_width=True)
                    
                    if prediction.get('is_anomaly'):
                        st.warning(f"⚠️ **Anomaly Detected!** This match has an anomaly score of {prediction['anomaly_score']:.2f}, which may indicate unusual betting patterns or market activity.")
                    
                    with st.expander("📋 Detailed Prediction Data"):
                        st.json(prediction)
                
                else:
                    st.error(f"❌ Prediction failed: {response.text}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running on port 8000.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with tab2:
    st.header("Tournament Monte Carlo Simulation")
    st.markdown("**Simulates full FIFA 2026 48-team format using goal-based predictions**")
    
    num_sims = st.slider(
        "Number of Simulations",
        min_value=1000,
        max_value=50000,
        value=10000,
        step=1000,
        help="More simulations = more accurate probabilities"
    )
    
    if st.button("🎲 Run Tournament Simulation", type="primary", use_container_width=True):
        with st.spinner(f"Running {num_sims:,} Monte Carlo simulations..."):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/simulate_tournament",
                    json={
                        "num_simulations": num_sims,
                        "tournament_format": "FIFA_2026"
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    results = response.json()
                    
                    st.success(f"✅ Completed {num_sims:,} simulations in {results['simulation_time_seconds']}s")
                    
                    col_sim1, col_sim2 = st.columns(2)
                    
                    with col_sim1:
                        st.subheader("🥇 Winner Probabilities")
                        winner_df = pd.DataFrame([
                            {"Team": team, "Probability": prob * 100}
                            for team, prob in list(results['winner_probabilities'].items())[:10]
                        ])
                        
                        fig_winners = px.bar(
                            winner_df,
                            x="Team",
                            y="Probability",
                            title="Top 10 Teams Most Likely to Win",
                            labels={"Probability": "Win Probability (%)"}
                        )
                        st.plotly_chart(fig_winners, use_container_width=True)
                    
                    with col_sim2:
                        st.subheader("🥈 Finalist Probabilities")
                        finalist_df = pd.DataFrame([
                            {"Team": team, "Probability": prob * 100}
                            for team, prob in list(results['finalist_probabilities'].items())[:10]
                        ])
                        
                        fig_finalists = px.bar(
                            finalist_df,
                            x="Team",
                            y="Probability",
                            title="Top 10 Teams Most Likely to Reach Final",
                            labels={"Probability": "Finalist Probability (%)"}
                        )
                        st.plotly_chart(fig_finalists, use_container_width=True)
                
                else:
                    st.error(f"❌ Simulation failed: {response.text}")
            
            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure the FastAPI server is running.")
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

with tab3:
    st.header("Match Context Intelligence")
    st.markdown("**Weather, Referee Stats, Travel Data**")
    
    fixture_id = st.number_input("Fixture ID", min_value=1, value=1, step=1)
    
    if st.button("📍 Get Match Context", use_container_width=True):
        try:
            response = requests.get(
                f"{API_BASE_URL}/fixture/{fixture_id}/context",
                timeout=10
            )
            
            if response.status_code == 200:
                context = response.json()
                
                col_ctx1, col_ctx2, col_ctx3 = st.columns(3)
                
                with col_ctx1:
                    st.subheader("🌤️ Weather")
                    if context.get('weather'):
                        weather = context['weather']
                        st.metric("Temperature", f"{weather.get('temperature', 'N/A')}°C")
                        st.metric("Humidity", f"{weather.get('humidity', 'N/A')}%")
                        st.metric("Wind Speed", f"{weather.get('wind_speed', 'N/A')} km/h")
                        st.write(f"**Conditions:** {weather.get('conditions', 'Clear')}")
                    else:
                        st.info("No weather data available")
                
                with col_ctx2:
                    st.subheader("🎗️ Referee")
                    if context.get('referee'):
                        ref = context['referee']
                        st.write(f"**Name:** {ref['name']}")
                        st.metric("Avg Cards/Match", f"{ref['avg_cards_per_match']:.1f}")
                        st.metric("Home Win Bias", f"{ref['home_win_bias_pct']:.1f}%")
                        st.metric("Matches Officiated", ref['total_matches_officiated'])
                    else:
                        st.info("No referee data available")
                
                with col_ctx3:
                    st.subheader("✈️ Travel")
                    home_dist = context.get('home_travel_distance_km')
                    away_dist = context.get('away_travel_distance_km')
                    
                    if home_dist or away_dist:
                        st.metric("Home Team Distance", f"{home_dist or 0:.0f} km")
                        st.metric("Away Team Distance", f"{away_dist or 0:.0f} km")
                        st.metric("Home Timezones", context.get('home_timezones_crossed', 0))
                        st.metric("Away Timezones", context.get('away_timezones_crossed', 0))
                    else:
                        st.info("No travel data available")
            
            else:
                st.error(f"❌ Failed to get context: {response.text}")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

with tab4:
    st.header("🚨 Real-Time Injury & Suspension Alerts")
    st.markdown("**NLP-Detected from News Articles**")
    
    st.info("This feature shows players flagged as injured or suspended by the NLP injury detection system.")
    
    st.markdown("""
    **How it works:**
    - Automated scanning of news articles daily
    - spaCy NER model identifies player names
    - Pattern matching for injury/suspension keywords
    - Confidence scoring for each detection
    """)
    
    st.warning("⚠️ Sample data shown. Connect to database for live injury reports.")

with tab5:
    st.header("📈 Model Explainability (XAI)")
    st.markdown("**SHAP Feature Importance & Prediction Explanation**")
    
    match_id = st.number_input("Match ID for Explainability", min_value=1, value=1, step=1)
    
    if st.button("🔍 Get Explanation", use_container_width=True):
        try:
            response = requests.get(
                f"{API_BASE_URL}/get_match_explainability/{match_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                explain = response.json()
                
                st.subheader("Why This Prediction?")
                st.info(explain.get('explanation_text', 'No explanation available'))
                
                if explain.get('top_features'):
                    st.subheader("Top Feature Contributions")
                    
                    features_df = pd.DataFrame(explain['top_features'])
                    
                    fig_importance = px.bar(
                        features_df.head(10),
                        x='importance',
                        y='feature',
                        orientation='h',
                        title="Top 10 Most Important Features",
                        labels={'importance': 'Feature Impact', 'feature': 'Feature Name'}
                    )
                    st.plotly_chart(fig_importance, use_container_width=True)
                
                with st.expander("📊 All Feature Importance Values"):
                    st.json(explain.get('feature_importance', {}))
            
            else:
                st.warning(f"No explainability data found for match {match_id}")
        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown("**System Status:** 🟢 Operational | **Model Version:** v3.0 Dual-Regression | **Target Accuracy:** 80%+")
st.markdown("*Using player-level xG/xA data, NLP injury detection, market values, and advanced feature engineering*")
