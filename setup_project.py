# setup_project.py - FIXED VERSION
import os
import sys

def create_file(path, content):
    """Create a file with given content"""
    # Handle root directory files (like requirements.txt)
    dirname = os.path.dirname(path)
    if dirname:  # Only create directory if it's not empty
        os.makedirs(dirname, exist_ok=True)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created: {path}")

print("🚗 Setting up CarSafe project files...")

# Create all required files
files = {
    "src/__init__.py": "# CarSafe package\n",
    
    "src/api/__init__.py": "# API module\n",
    
    "src/database/__init__.py": "# Database module\n",
    "src/database/setup.py": '''# src/database/setup.py
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages PostgreSQL database setup and connections"""
    
    def __init__(self, 
                 host='localhost', 
                 port=5432, 
                 database='carsafe',
                 user='postgres', 
                 password='postgres'):
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None
        logger.info("DatabaseManager initialized")
        
    def connect(self):
        """Establish database connection"""
        logger.info("Connecting to database...")
        return True
    
    def setup_tables(self):
        """Create necessary tables"""
        logger.info("Setting up database tables...")
        return True
    
    def insert_telemetry(self, telemetry_data: dict):
        """Insert telemetry data into database"""
        logger.info(f"Inserting telemetry for vehicle {telemetry_data.get('vehicle_id', 'unknown')}")
        return 1
    
    def insert_fault(self, fault_data: dict):
        """Insert fault data into database"""
        logger.info(f"Inserting fault {fault_data.get('fault', {}).get('code', 'unknown')}")
        return 1
    
    def get_recent_telemetry(self, vehicle_id: str = None, limit: int = 100):
        """Get recent telemetry data"""
        logger.info(f"Getting recent telemetry for {vehicle_id or 'all vehicles'}")
        return []
    
    def close(self):
        """Close database connection"""
        logger.info("Database connection closed")
''',
    
    "src/kafka_client/__init__.py": "# Kafka client module\n",
    "src/kafka_client/producer.py": '''# src/kafka_client/producer.py
import json
import logging

logger = logging.getLogger(__name__)

class VehicleDataProducer:
    """Kafka producer for vehicle telemetry data"""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        logger.info(f"VehicleDataProducer initialized for {bootstrap_servers}")
    
    def connect(self):
        """Establish connection to Kafka"""
        logger.info("Connecting to Kafka...")
        return True
    
    def send_custom_message(self, topic: str, message: dict):
        """Send a custom message to Kafka"""
        logger.info(f"Sending message to topic '{topic}': {json.dumps(message)[:100]}...")
        return True
    
    def close(self):
        """Close producer connection"""
        logger.info("Kafka producer closed")
''',
    
    "src/kafka_client/consumer.py": '''# src/kafka_client/consumer.py
import logging

logger = logging.getLogger(__name__)

class VehicleDataConsumer:
    """Kafka consumer for vehicle telemetry data"""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        logger.info(f"VehicleDataConsumer initialized for {bootstrap_servers}")
''',
    
    "src/anomaly_detection/__init__.py": "# Anomaly detection module\n",
    "src/anomaly_detection/detector.py": '''# src/anomaly_detection/detector.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AnomalyDetector:
    """Detects anomalies in vehicle telemetry data"""
    
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        logger.info(f"AnomalyDetector initialized with contamination={contamination}")
    
    def detect_single_point(self, telemetry_data: dict):
        """Detect anomalies in a single telemetry point"""
        logger.info(f"Detecting anomalies for vehicle {telemetry_data.get('vehicle_id', 'unknown')}")
        return {
            'is_anomaly': False,
            'confidence': 0.0,
            'anomaly_type': 'none'
        }
    
    def detect_batch(self, vehicle_id: str, start_time: datetime, end_time: datetime):
        """Detect anomalies in a batch of historical data"""
        logger.info(f"Batch anomaly detection for {vehicle_id} from {start_time} to {end_time}")
        return []
''',
    
    "src/data_generator/__init__.py": "# Data generator module\n",
    "src/data_generator/can_bus_simulator.py": '''# src/data_generator/can_bus_simulator.py
import random
from datetime import datetime

class CANBusSimulator:
    """Simulates CAN bus data from vehicles"""
    
    def __init__(self, vehicle_id: str, make: str = "Toyota", model: str = "Camry"):
        self.vehicle_id = vehicle_id
        self.make = make
        self.model = model
    
    def generate_telemetry(self):
        """Generate realistic vehicle telemetry data"""
        return {
            'vehicle_id': self.vehicle_id,
            'telemetry': {
                'timestamp': datetime.now(),
                'speed': random.uniform(0, 120),
                'rpm': random.uniform(800, 4000),
                'throttle': random.uniform(0, 100),
                'brake': random.uniform(0, 100),
                'engine_temp': random.uniform(85, 105),
                'fuel_level': random.uniform(10, 100),
                'latitude': 35.6895 + random.uniform(-0.01, 0.01),
                'longitude': 139.6917 + random.uniform(-0.01, 0.01),
                'odometer': random.uniform(1000, 50000)
            }
        }
''',
    
    "src/utils/__init__.py": "# Utilities module\n",
    "tests/__init__.py": "# Tests module\n",
    
    "dashboard/app.py": '''# dashboard/app.py
import streamlit as st

st.set_page_config(
    page_title="CarSafe Dashboard",
    page_icon="🚗",
    layout="wide"
)

st.title("🚗 CarSafe Dashboard")
st.write("Vehicle telemetry monitoring system")
'''
}

# Create all files
for file_path, content in files.items():
    create_file(file_path, content)

# Create requirements.txt separately (root directory file)
requirements_content = '''# Core dependencies
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Data processing
pandas==1.5.3
numpy==1.24.3
scikit-learn==1.3.2

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.23

# Streaming
kafka-python==2.0.2

# Dashboard
streamlit==1.28.1
plotly==5.18.0

# Testing
pytest==7.4.4
'''

with open("requirements.txt", 'w', encoding='utf-8') as f:
    f.write(requirements_content)
print("✓ Created: requirements.txt")

print("\n✅ All project files created successfully!")
print("\nNext steps:")
print("1. Install dependencies: pip install -r requirements.txt")
print("2. Run the API: uvicorn src.api.main:app --reload")
print("3. Open: http://localhost:8000/docs")