import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import time
import random

# Configure page
st.set_page_config(page_title="Global Weather Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS
st.markdown("""
    <style>
        .reportview-container {
            background: #f0f2f6
        }
        .big-font {
            font-size:24px !important;
            font-weight: bold;
        }
        .metric-card {
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin: 10px;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Generate sample data for production
@st.cache_data
def generate_sample_data():
    regions = ["New York", "London", "Tokyo", "Mumbai", "Sydney", "Paris", "Dubai", "Singapore"]
    data = []
    
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        for region in regions:
            data.append({
                "date": date,
                "region": region,
                "temperature": round(random.uniform(15, 35), 1),
                "humidity": round(random.uniform(30, 90)),
                "wind_speed": round(random.uniform(0, 30), 1),
                "air_quality_index": round(random.uniform(20, 150)),
                "precipitation": round(random.uniform(0, 100), 2)
            })
    return data

# Title with style
st.markdown("<h1 style='text-align: center;'>🌍 Global Weather Intelligence Dashboard</h1>", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📊 Dashboard Controls")
    
    # Date Range Selection
    st.subheader("Date Selection")
    selected_date = st.date_input(
        "Select Date",
        datetime.now(),
        min_value=datetime.now() - timedelta(days=30),
        max_value=datetime.now()
    )
    
    # Region Selection
    st.subheader("Region Filter")
    sample_data = generate_sample_data()
    regions = sorted(list(set(d["region"] for d in sample_data)))
    selected_region = st.selectbox("Select Region", ["All Regions"] + regions)
    
    # Refresh Rate
    st.subheader("Refresh Settings")
    auto_refresh = st.checkbox("Auto Refresh")
    if auto_refresh:
        refresh_interval = st.slider("Refresh Interval (seconds)", 5, 60, 30)

def load_weather_data():
    try:
        # In production, use generated data
        data = generate_sample_data()
        
        # Filter data based on selection
        filtered_data = [d for d in data if d['date'] == selected_date.strftime('%Y-%m-%d')]
        if selected_region != "All Regions":
            filtered_data = [d for d in filtered_data if d['region'] == selected_region]
        
        if not filtered_data:
            st.warning("No data found for the selected filters.")
            return pd.DataFrame()
            
        return pd.DataFrame(filtered_data)
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return pd.DataFrame()

# Main dashboard area
def create_dashboard():
    weather_df = load_weather_data()
    
    if not weather_df.empty:
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                f"""<div class='metric-card'>
                    <h3>Average Temperature</h3>
                    <p class='big-font'>{weather_df['temperature'].mean():.1f}°C</p>
                </div>""", 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                f"""<div class='metric-card'>
                    <h3>Average Humidity</h3>
                    <p class='big-font'>{weather_df['humidity'].mean():.1f}%</p>
                </div>""",
                unsafe_allow_html=True
            )
            
        with col3:
            st.markdown(
                f"""<div class='metric-card'>
                    <h3>Average Wind Speed</h3>
                    <p class='big-font'>{weather_df['wind_speed'].mean():.1f} km/h</p>
                </div>""",
                unsafe_allow_html=True
            )
            
        with col4:
            st.markdown(
                f"""<div class='metric-card'>
                    <h3>Average AQI</h3>
                    <p class='big-font'>{weather_df['air_quality_index'].mean():.1f}</p>
                </div>""",
                unsafe_allow_html=True
            )

        # Main visualizations
        tab1, tab2, tab3 = st.tabs(["Temperature Analysis", "Weather Metrics", "Data View"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                # Temperature Map
                fig_temp = px.bar(weather_df,
                                x='region',
                                y='temperature',
                                color='temperature',
                                title='Temperature Distribution by Region',
                                color_continuous_scale='RdYlBu_r')
                st.plotly_chart(fig_temp, use_container_width=True)
            
            with col2:
                # Temperature vs Humidity
                fig_temp_humidity = px.scatter(weather_df,
                                            x='temperature',
                                            y='humidity',
                                            color='region',
                                            size='wind_speed',
                                            title='Temperature vs Humidity Analysis')
                st.plotly_chart(fig_temp_humidity, use_container_width=True)

        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Wind Speed Analysis
                fig_wind = px.bar(weather_df,
                                x='region',
                                y='wind_speed',
                                color='wind_speed',
                                title='Wind Speed by Region',
                                color_continuous_scale='Viridis')
                st.plotly_chart(fig_wind, use_container_width=True)
            
            with col2:
                # Air Quality Index
                fig_aqi = px.scatter(weather_df,
                                   x='region',
                                   y='air_quality_index',
                                   size='temperature',
                                   color='air_quality_index',
                                   title='Air Quality Index by Region',
                                   color_continuous_scale='RdYlGn_r')
                st.plotly_chart(fig_aqi, use_container_width=True)

        with tab3:
            st.subheader("Raw Data View")
            st.dataframe(weather_df, use_container_width=True)
            
            # Download button
            csv = weather_df.to_csv(index=False)
            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name=f'weather_data_{selected_date}.csv',
                mime='text/csv'
            )

# Main loop for auto refresh
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = time.time()

if auto_refresh:
    if time.time() - st.session_state.last_refresh > refresh_interval:
        st.session_state.last_refresh = time.time()
        st.experimental_rerun()

create_dashboard()

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center;'>🌡️ Global Weather Intelligence Dashboard | Last Updated: "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
    unsafe_allow_html=True
)