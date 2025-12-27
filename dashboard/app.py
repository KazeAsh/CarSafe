# dashboard/app.py
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time

# Page configuration
st.set_page_config(
    page_title="CarSafe Dashboard",
    page_icon="🚗",
    layout="wide"
)

# API URL
API_URL = "http://localhost:8000"

@st.cache_data(ttl=10)  # Cache for 10 seconds
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
        vehicle_count = len(set([t.get("vehicle_id", "") for t in telemetry_data]))
        st.metric("Active Vehicles", vehicle_count)
    
    with col2:
        st.metric("Telemetry Points", len(telemetry_data))
    
    with col3:
        active_faults = len([f for f in fault_data if not f.get("resolved", False)])
        st.metric("Active Faults", active_faults, delta_color="inverse")
    
    with col4:
        if telemetry_data:
            avg_speed = sum(t.get("speed", 0) for t in telemetry_data) / len(telemetry_data)
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
            
            # Convert timestamp
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.sort_values("timestamp", ascending=False)
            
            # Show data
            st.subheader("Recent Telemetry Data")
            st.dataframe(df[["vehicle_id", "timestamp", "speed", "rpm", "engine_temp"]].head(10), 
                        use_container_width=True)
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                if len(df) > 1:
                    fig = px.line(df, x="timestamp", y="speed", color="vehicle_id",
                                 title="Speed Over Time")
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if "vehicle_id" in df.columns:
                    vehicle_speeds = df.groupby("vehicle_id")["speed"].mean().reset_index()
                    fig = px.bar(vehicle_speeds, x="vehicle_id", y="speed",
                                title="Average Speed by Vehicle")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No telemetry data available. Start the data generator!")
    
    with tab2:
        if fault_data:
            df_faults = pd.DataFrame(fault_data)
            
            # Show active faults first
            active_faults_df = df_faults[~df_faults.get("resolved", True)]
            
            st.subheader("Active Faults")
            if not active_faults_df.empty:
                st.dataframe(active_faults_df[["vehicle_id", "fault_code", "severity", "timestamp"]], 
                           use_container_width=True)
                
                # Severity distribution
                severity_counts = active_faults_df["severity"].value_counts().reset_index()
                severity_counts.columns = ["severity", "count"]
                
                fig = px.pie(severity_counts, values="count", names="severity",
                           title="Fault Severity Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.success("No active faults! ✅")
            
            # Show all faults
            st.subheader("All Faults")
            st.dataframe(df_faults, use_container_width=True)
        else:
            st.info("No fault data available.")
    
    with tab3:
        st.subheader("Registered Vehicles")
        
        # Try to get vehicles from API
        try:
            response = requests.get(f"{API_URL}/api/vehicles", timeout=5)
            if response.status_code == 200:
                vehicles = response.json().get("data", [])
                if vehicles:
                    df_vehicles = pd.DataFrame(vehicles)
                    st.dataframe(df_vehicles, use_container_width=True)
                else:
                    st.info("No vehicles registered.")
            else:
                st.info("Vehicle endpoint not available.")
        except:
            # Show sample vehicles
            sample_vehicles = [
                {"vehicle_id": "VH0001", "make": "Toyota", "model": "Camry", "year": 2023},
                {"vehicle_id": "VH0002", "make": "Toyota", "model": "Prius", "year": 2022},
                {"vehicle_id": "VH0003", "make": "Lexus", "model": "RX", "year": 2023}
            ]
            st.dataframe(pd.DataFrame(sample_vehicles), use_container_width=True)
            st.caption("Sample data - implement vehicle registration to see real data")
    
    # Sidebar controls
    with st.sidebar:
        st.header("Controls")
        
        # Data generator control
        if st.button("▶️ Start Data Generator", use_container_width=True):
            st.info("Run: python src/data_generator/main.py")
        
        if st.button("⏹️ Stop Data Generator", use_container_width=True):
            st.info("Press Ctrl+C in the data generator terminal")
        
        st.divider()
        
        # Manual data entry
        st.header("Manual Entry")
        
        with st.form("manual_telemetry"):
            st.subheader("Add Telemetry")
            vehicle_id = st.text_input("Vehicle ID", "VH0001")
            speed = st.slider("Speed (km/h)", 0, 200, 65)
            rpm = st.slider("RPM", 0, 8000, 2500)
            
            if st.form_submit_button("Send Telemetry"):
                telemetry = {
                    "vehicle_id": vehicle_id,
                    "timestamp": datetime.now().isoformat(),
                    "speed": speed,
                    "rpm": rpm,
                    "throttle": 35.0,
                    "brake": 0.0,
                    "engine_temp": 92.5,
                    "fuel_level": 78.0,
                    "latitude": 35.6895,
                    "longitude": 139.6917,
                    "odometer": 12345.6
                }
                
                try:
                    response = requests.post(f"{API_URL}/api/telemetry", json=telemetry)
                    if response.status_code == 201:
                        st.success("Telemetry sent!")
                    else:
                        st.error(f"Failed: {response.status_code}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.divider()
        st.caption(f"Last updated: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()