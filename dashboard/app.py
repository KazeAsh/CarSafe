import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json

# Page configuration
st.set_page_config(
    page_title="Vehicle Data Pipeline Dashboard",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #3B82F6;
    }
    .anomaly-card {
        background-color: #FEF2F2;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #DC2626;
    }
</style>
""", unsafe_allow_html=True)

# API URL
API_URL = "http://localhost:8000"

def main():
    """Main dashboard application"""
    
    # Header
    st.markdown('<h1 class="main-header">🚗 Vehicle Data Pipeline Dashboard</h1>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50/3B82F6/FFFFFF?text=Toyota+Data", 
                 use_column_width=True)
        
        st.markdown("### Navigation")
        page = st.radio(
            "Select Page",
            ["📊 Overview", "🚘 Vehicle Details", "⚠️ Anomalies", "🔧 Pipeline Status", "📈 Analytics"]
        )
        
        st.markdown("---")
        st.markdown("### Quick Actions")
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.rerun()
        
        if st.button("🚨 Test Emergency", use_container_width=True):
            st.session_state.test_emergency = True
            st.success("Test emergency triggered!")
        
        st.markdown("---")
        st.markdown("### Filters")
        
        vehicle_filter = st.selectbox(
            "Select Vehicle",
            ["All Vehicles", "VH0001", "VH0002", "VH0003", "VH0004", "VH0005"]
        )
        
        time_filter = st.select_slider(
            "Time Range",
            options=["1h", "6h", "12h", "24h", "48h"],
            value="24h"
        )
    
    # Main content based on selected page
    if page == "📊 Overview":
        show_overview(vehicle_filter, time_filter)
    elif page == "🚘 Vehicle Details":
        show_vehicle_details(vehicle_filter)
    elif page == "⚠️ Anomalies":
        show_anomalies()
    elif page == "🔧 Pipeline Status":
        show_pipeline_status()
    elif page == "📈 Analytics":
        show_analytics()

def show_overview(vehicle_filter, time_filter):
    """Show overview dashboard"""
    
    # Metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🚘 Active Vehicles</h3>
            <h2>12</h2>
            <p>+2 this week</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Data Points</h3>
            <h2>1.2M</h2>
            <p>Today: 45,230</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚠️ Active Faults</h3>
            <h2 style="color: #DC2626;">3</h2>
            <p>2 High, 1 Medium</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Accuracy</h3>
            <h2>99.3%</h2>
            <p>Anomaly detection</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Charts row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Vehicle Speed Distribution")
        
        # Generate sample data
        speed_data = pd.DataFrame({
            'Vehicle': [f'VH{i:04d}' for i in range(1, 11)],
            'Avg Speed': [65 + i*2 for i in range(10)],
            'Max Speed': [120 + i*5 for i in range(10)]
        })
        
        fig = go.Figure(data=[
            go.Bar(name='Average Speed', x=speed_data['Vehicle'], y=speed_data['Avg Speed']),
            go.Bar(name='Maximum Speed', x=speed_data['Vehicle'], y=speed_data['Max Speed'])
        ])
        
        fig.update_layout(
            barmode='group',
            height=400,
            showlegend=True,
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🌡️ Engine Temperature Trends")
        
        # Generate time series data
        time_series = pd.DataFrame({
            'Time': pd.date_range(start='2024-01-15 00:00', periods=24, freq='H'),
            'Temperature': [90 + i%5 for i in range(24)]
        })
        
        fig = px.line(time_series, x='Time', y='Temperature', 
                     title='24-Hour Engine Temperature')
        fig.update_layout(height=400, plot_bgcolor='rgba(0,0,0,0)')
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent anomalies
    st.markdown("---")
    st.subheader("🚨 Recent Anomalies")
    
    anomalies_data = pd.DataFrame({
        'Time': ['10:30', '09:15', '08:45', '07:20', '06:50'],
        'Vehicle': ['VH0003', 'VH0001', 'VH0002', 'VH0004', 'VH0001'],
        'Type': ['Sudden Braking', 'Engine Overheat', 'High RPM', 'Low Fuel', 'Abnormal Throttle'],
        'Severity': ['HIGH', 'HIGH', 'MEDIUM', 'MEDIUM', 'LOW'],
        'Confidence': [0.92, 0.88, 0.76, 0.65, 0.52]
    })
    
    for _, row in anomalies_data.iterrows():
        severity_color = {
            'HIGH': '#DC2626',
            'MEDIUM': '#F59E0B',
            'LOW': '#10B981'
        }.get(row['Severity'], '#6B7280')
        
        st.markdown(f"""
        <div class="anomaly-card">
            <div style="display: flex; justify-content: space-between;">
                <div>
                    <strong>{row['Type']}</strong> • {row['Vehicle']}
                </div>
                <div style="color: {severity_color};">
                    {row['Severity']} • {row['Confidence']*100:.0f}% conf
                </div>
            </div>
            <div style="color: #6B7280; font-size: 0.9rem;">
                Detected at {row['Time']}
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_vehicle_details(vehicle_filter):
    """Show detailed vehicle information"""
    
    st.header(f"🚘 Vehicle Details: {vehicle_filter}")
    
    if vehicle_filter == "All Vehicles":
        st.info("Select a specific vehicle from the sidebar to view detailed information.")
        return
    
    # Vehicle info card
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://via.placeholder.com/300x200/3B82F6/FFFFFF?text=Vehicle+Image", 
                 use_container_width=True)
        
        st.metric("Current Speed", "68.5 km/h", "+2.3")
        st.metric("Engine Temp", "92.5°C", "-0.5")
        st.metric("Fuel Level", "78.2%", "-1.8")
    
    with col2:
        st.subheader("Real-time Metrics")
        
        # Create tabs for different metrics
        tab1, tab2, tab3 = st.tabs(["📊 Telemetry", "⚠️ Fault History", "📈 Trends"])
        
        with tab1:
            # Generate sample telemetry data
            telemetry_data = pd.DataFrame({
                'Parameter': ['Speed', 'RPM', 'Throttle', 'Brake', 'Engine Temp', 'Fuel'],
                'Value': [68.5, 2450, 35.2, 0.0, 92.5, 78.2],
                'Unit': ['km/h', 'RPM', '%', '%', '°C', '%'],
                'Status': ['Normal', 'Normal', 'Normal', 'Normal', 'Warning', 'Normal']
            })
            
            for _, row in telemetry_data.iterrows():
                status_color = '🟢' if row['Status'] == 'Normal' else '🟡'
                st.write(f"{status_color} **{row['Parameter']}:** {row['Value']} {row['Unit']}")
        
        with tab2:
            faults = pd.DataFrame({
                'Date': ['2024-01-14', '2024-01-10', '2024-01-05'],
                'Code': ['P0300', 'P0420', 'P0171'],
                'Description': ['Cylinder Misfire', 'Catalyst Efficiency', 'System Too Lean'],
                'Severity': ['HIGH', 'MEDIUM', 'LOW'],
                'Status': ['Active', 'Resolved', 'Resolved']
            })
            
            st.dataframe(faults, use_container_width=True)
        
        with tab3:
            # Generate trend data
            trend_data = pd.DataFrame({
                'Hour': list(range(24)),
                'Speed': [60 + i%10 for i in range(24)],
                'RPM': [2200 + i%500 for i in range(24)],
                'Temp': [90 + i%5 for i in range(24)]
            })
            
            fig = px.line(trend_data, x='Hour', y=['Speed', 'RPM', 'Temp'],
                         title='24-Hour Trends')
            st.plotly_chart(fig, use_container_width=True)

def show_anomalies():
    """Show anomaly detection dashboard"""
    
    st.header("⚠️ Anomaly Detection Center")
    
    # Anomaly summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Detected", "24", "+3 today")
    
    with col2:
        st.metric("High Severity", "5", "Needs attention")
    
    with col3:
        st.metric("False Positive Rate", "2.3%", "-0.5%")
    
    st.markdown("---")
    
    # Anomaly types breakdown
    st.subheader("Anomaly Types Distribution")
    
    anomaly_types = pd.DataFrame({
        'Type': ['Sudden Braking', 'Engine Overheat', 'High RPM', 'Low Fuel', 'Other'],
        'Count': [8, 5, 4, 3, 4],
        'Avg Confidence': [0.89, 0.92, 0.76, 0.65, 0.58]
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.pie(anomaly_types, values='Count', names='Type', 
                     title='Anomaly Type Distribution')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(anomaly_types, x='Type', y='Avg Confidence',
                     title='Average Confidence by Type')
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed anomaly list
    st.subheader("Detailed Anomaly Log")
    
    anomalies = pd.DataFrame({
        'Timestamp': pd.date_range(start='2024-01-15', periods=10, freq='H'),
        'Vehicle': ['VH0001', 'VH0003', 'VH0002', 'VH0001', 'VH0004',
                   'VH0005', 'VH0002', 'VH0003', 'VH0001', 'VH0004'],
        'Type': ['Sudden Braking', 'Engine Overheat', 'High RPM', 'Low Fuel', 'Sudden Braking',
                'Abnormal Throttle', 'Engine Overheat', 'High RPM', 'Low Fuel', 'Sudden Braking'],
        'Severity': ['HIGH', 'HIGH', 'MEDIUM', 'MEDIUM', 'HIGH',
                    'LOW', 'HIGH', 'MEDIUM', 'MEDIUM', 'HIGH'],
        'Confidence': [0.92, 0.88, 0.76, 0.65, 0.91,
                      0.52, 0.87, 0.71, 0.68, 0.93],
        'Status': ['Investigating', 'Resolved', 'Resolved', 'Investigating', 'Alerted',
                  'Resolved', 'Investigating', 'Resolved', 'Alerted', 'Investigating']
    })
    
    st.dataframe(anomalies.sort_values('Timestamp', ascending=False), 
                 use_container_width=True)

def show_pipeline_status():
    """Show data pipeline status"""
    
    st.header("🔧 Data Pipeline Status")
    
    # Pipeline components status
    components = [
        {"name": "Kafka Broker", "status": "🟢 Running", "uptime": "99.8%"},
        {"name": "Data Producers", "status": "🟢 Active", "throughput": "1,200 msg/s"},
        {"name": "Stream Processors", "status": "🟢 Normal", "lag": "0.2s"},
        {"name": "Database", "status": "🟢 Connected", "size": "2.4 GB"},
        {"name": "API Server", "status": "🟢 Online", "response": "45 ms"},
        {"name": "ML Service", "status": "🟡 Warning", "load": "85%"}
    ]
    
    for component in components:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.write(f"**{component['name']}**")
        with col2:
            st.write(component['status'])
        with col3:
            st.caption(component.get('uptime', component.get('throughput', '')))
        st.progress(85 if component['name'] == "ML Service" else 100)
    
    st.markdown("---")
    
    # Throughput metrics
    st.subheader("📊 Pipeline Throughput")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Messages/sec", "1,245", "+125")
    
    with col2:
        st.metric("Processing Latency", "0.23s", "-0.05s")
    
    with col3:
        st.metric("Error Rate", "0.03%", "±0.01%")
    
    # Throughput chart
    throughput_data = pd.DataFrame({
        'Hour': list(range(24)),
        'Messages': [800 + i*50 + (i%3)*100 for i in range(24)],
        'Processing Time': [0.15 + i*0.01 for i in range(24)]
    })
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=throughput_data['Hour'], y=throughput_data['Messages'],
                            name='Messages/sec', yaxis='y'))
    fig.add_trace(go.Scatter(x=throughput_data['Hour'], y=throughput_data['Processing Time'],
                            name='Processing Time (s)', yaxis='y2'))
    
    fig.update_layout(
        title='24-Hour Pipeline Performance',
        yaxis=dict(title='Messages/sec'),
        yaxis2=dict(title='Processing Time (s)', overlaying='y', side='right'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_analytics():
    """Show advanced analytics"""
    
    st.header("📈 Advanced Analytics")
    
    # Model performance
    st.subheader("🤖 ML Model Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Accuracy", "98.7%", "+0.3%")
    
    with col2:
        st.metric("Precision", "96.2%", "+0.8%")
    
    with col3:
        st.metric("Recall", "95.8%", "+1.2%")
    
    # ROC Curve (simulated)
    st.subheader("Model ROC Curve")
    
    # Generate synthetic ROC data
    fpr = [i/100 for i in range(101)]
    tpr = [min(1, i/100 * 1.2) for i in range(101)]  # Simulated ROC
    
    roc_data = pd.DataFrame({'FPR': fpr, 'TPR': tpr})
    
    fig = px.line(roc_data, x='FPR', y='TPR', 
                  title='Receiver Operating Characteristic (ROC) Curve')
    fig.add_shape(type='line', line=dict(dash='dash'),
                  x0=0, y0=0, x1=1, y1=1)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Feature importance
    st.subheader("Feature Importance")
    
    features = pd.DataFrame({
        'Feature': ['Speed Delta', 'Brake Pressure', 'RPM Variance', 
                   'Engine Temp', 'Throttle-Brake Diff', 'Fuel Rate'],
        'Importance': [0.28, 0.22, 0.18, 0.15, 0.10, 0.07]
    })
    
    fig = px.bar(features.sort_values('Importance'), 
                 x='Importance', y='Feature', orientation='h',
                 title='Anomaly Detection Feature Importance')
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()