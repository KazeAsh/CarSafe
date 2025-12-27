# dashboard/app.py - FIXED VERSION
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# Page configuration
st.set_page_config(
    page_title="CarSafe Dashboard",
    page_icon="🚗",
    layout="wide"
)

# API URL
API_URL = "http://localhost:8000"

@st.cache_data(ttl=5)  # Cache for 5 seconds
def fetch_telemetry(limit=100):
    """Fetch telemetry data from API"""
    try:
        response = requests.get(f"{API_URL}/api/telemetry?limit={limit}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
    except:
        pass
    return []

@st.cache_data(ttl=10)
def fetch_faults():
    """Fetch fault data from API"""
    try:
        response = requests.get(f"{API_URL}/api/faults", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("data", [])
    except:
        pass
    return []

@st.cache_data(ttl=30)
def fetch_health():
    """Check API health"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title("🚗 CarSafe Dashboard")
        st.markdown("Real-time vehicle telemetry monitoring system")
    
    with col2:
        # Health status
        is_healthy = fetch_health()
        status_color = "🟢" if is_healthy else "🔴"
        status_text = "Connected" if is_healthy else "Disconnected"
        st.metric("API Status", f"{status_color} {status_text}")
        
        # Refresh button
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    st.divider()
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    # Fetch data
    telemetry_data = fetch_telemetry(50)
    fault_data = fetch_faults()
    
    with col1:
        if telemetry_data:
            vehicle_count = len(set([t.get("vehicle_id", "") for t in telemetry_data]))
            st.metric("Active Vehicles", vehicle_count)
        else:
            st.metric("Active Vehicles", 0)
    
    with col2:
        st.metric("Telemetry Points", len(telemetry_data))
    
    with col3:
        if fault_data:
            # Count active faults (where resolved is False or doesn't exist)
            active_faults = 0
            for fault in fault_data:
                if not fault.get("resolved", False):  # Default to False if key doesn't exist
                    active_faults += 1
            st.metric("Active Faults", active_faults, delta_color="inverse")
        else:
            st.metric("Active Faults", 0)
    
    with col4:
        if telemetry_data:
            speeds = [t.get("speed", 0) for t in telemetry_data]
            avg_speed = sum(speeds) / len(speeds) if speeds else 0
            st.metric("Avg Speed", f"{avg_speed:.1f} km/h")
        else:
            st.metric("Avg Speed", "0 km/h")
    
    st.divider()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["📊 Telemetry", "⚠️ Faults", "🚘 Vehicles"])
    
    with tab1:
        if telemetry_data:
            # Convert to DataFrame
            df = pd.DataFrame(telemetry_data)
            
            # Show raw data
            st.subheader("Recent Telemetry Data")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Charts
            if len(df) > 1:
                col1, col2 = st.columns(2)
                
                with col1:
                    if 'speed' in df.columns:
                        fig = px.line(df, x=df.index, y='speed', title='Speed Over Time')
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if 'vehicle_id' in df.columns and 'speed' in df.columns:
                        vehicle_avg = df.groupby('vehicle_id')['speed'].mean().reset_index()
                        fig = px.bar(vehicle_avg, x='vehicle_id', y='speed', 
                                   title='Average Speed by Vehicle')
                        st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No telemetry data available. Start the data generator!")
    
    with tab2:
        if fault_data:
            df_faults = pd.DataFrame(fault_data)
            
            # Show all faults
            st.subheader("All Faults")
            st.dataframe(df_faults, use_container_width=True)
            
            # Show active faults separately
            if "resolved" in df_faults.columns:
                active_faults_df = df_faults[df_faults["resolved"] == False]
                
                st.subheader("Active Faults")
                if not active_faults_df.empty:
                    st.dataframe(active_faults_df, use_container_width=True)
                    
                    # Severity distribution
                    severity_counts = active_faults_df["severity"].value_counts().reset_index()
                    severity_counts.columns = ["severity", "count"]
                    
                    fig = px.pie(severity_counts, values="count", names="severity",
                               title="Active Faults by Severity")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.success("No active faults! ✅")
            else:
                st.info("No 'resolved' column in fault data")
        else:
            st.info("No fault data available.")
    
    with tab3:
        st.subheader("Registered Vehicles")
        
        # Try to get from API or show sample
        try:
            response = requests.get(f"{API_URL}/api/vehicles", timeout=5)
            if response.status_code == 200:
                vehicles = response.json().get("data", [])
                if vehicles:
                    df_vehicles = pd.DataFrame(vehicles)
                    st.dataframe(df_vehicles, use_container_width=True)
                else:
                    st.info("No vehicles registered via API.")
            else:
                # Show sample vehicles
                sample_vehicles = [
                    {"vehicle_id": "VH0001", "make": "Toyota", "model": "Camry", "year": 2023},
                    {"vehicle_id": "VH0002", "make": "Toyota", "model": "Prius", "year": 2022},
                    {"vehicle_id": "VH0003", "make": "Lexus", "model": "RX", "year": 2023}
                ]
                st.dataframe(pd.DataFrame(sample_vehicles), use_container_width=True)
                st.caption("Sample data - implement /api/vehicles endpoint for real data")
        except:
            st.error("Could not fetch vehicle data")
    
    # Auto-refresh
    time.sleep(10)
    st.rerun()

if __name__ == "__main__":
    main()