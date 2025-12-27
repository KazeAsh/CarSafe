# src/api/main.py - WORKING VERSION WITH MEMORY STORAGE
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime, timedelta
import uvicorn
import sys
import os

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
try:
    from src.database.setup import DatabaseManager
    from src.kafka_client.producer import VehicleDataProducer
    from src.kafka_client.consumer import VehicleDataConsumer
    from src.anomaly_detection.detector import AnomalyDetector
except ImportError:
    # Dummy implementations
    class DatabaseManager:
        def __init__(self): pass
        def connect(self): return True
        def setup_tables(self): pass
        def insert_telemetry(self, data): return 1
        def insert_fault(self, data): return 1
        def get_recent_telemetry(self, vid=None, limit=100): return []
        def close(self): pass
    
    class VehicleDataProducer:
        def __init__(self, servers='localhost:9092'): pass
        def send_custom_message(self, topic, message): 
            print(f"[Kafka] Sent to {topic} - {message.get('vehicle_id', 'unknown')}")
            return True
    
    class VehicleDataConsumer:
        def __init__(self, servers='localhost:9092'): pass
    
    class AnomalyDetector:
        def __init__(self, contamination=0.05): pass
        def detect_single_point(self, data): return {'is_anomaly': False}
        def detect_batch(self, vid, start, end): return []

# Initialize FastAPI app
app = FastAPI(
    title="CarSafe API",
    description="Vehicle Data Pipeline API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = DatabaseManager()
kafka_producer = VehicleDataProducer()
anomaly_detector = AnomalyDetector()

# In-memory storage (CRITICAL - this stores the data)
telemetry_store = []
fault_store = []

# Pydantic Models
class TelemetryData(BaseModel):
    vehicle_id: str
    timestamp: datetime
    speed: float = Field(..., ge=0, le=300)
    rpm: float = Field(..., ge=0, le=8000)
    throttle: float = Field(..., ge=0, le=100)
    brake: float = Field(..., ge=0, le=100)
    engine_temp: float = Field(..., ge=-40, le=150)
    fuel_level: float = Field(..., ge=0, le=100)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    odometer: float = Field(..., ge=0)

class FaultData(BaseModel):
    vehicle_id: str
    timestamp: datetime
    fault_code: str
    fault_description: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]

# Health check endpoint
@app.get("/")
async def root():
    return {
        "service": "CarSafe API",
        "status": "running",
        "records": len(telemetry_store),
        "endpoints": ["/health", "/api/telemetry", "/docs"]
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "storage": {"telemetry": len(telemetry_store), "faults": len(fault_store)}
    }

# Telemetry endpoints
@app.post("/api/telemetry", status_code=201)
async def add_telemetry(data: TelemetryData, background_tasks: BackgroundTasks):
    """Add telemetry data"""
    telemetry_dict = data.model_dump()
    
    # Store in memory (THIS IS WHAT WAS MISSING!)
    telemetry_store.append(telemetry_dict)
    
    # Keep only last 1000 records
    if len(telemetry_store) > 1000:
        telemetry_store.pop(0)
    
    print(f"📊 Stored: {telemetry_dict['vehicle_id']} - Speed: {telemetry_dict['speed']} km/h")
    
    # Background tasks
    background_tasks.add_task(
        kafka_producer.send_custom_message,
        topic="vehicle-telemetry",
        message=telemetry_dict
    )
    
    background_tasks.add_task(
        anomaly_detector.detect_single_point,
        telemetry_dict
    )
    
    return {
        "message": "Telemetry received",
        "vehicle_id": telemetry_dict['vehicle_id'],
        "total_records": len(telemetry_store)
    }

@app.get("/api/telemetry")
async def get_telemetry(
    vehicle_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get telemetry data"""
    results = telemetry_store.copy()
    
    if vehicle_id:
        results = [t for t in results if t.get('vehicle_id') == vehicle_id]
    
    # Sort by timestamp (newest first)
    results.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    results = results[:limit]
    
    print(f"📤 Returning {len(results)} records")
    
    return {
        "count": len(results),
        "vehicle_id": vehicle_id,
        "data": results
    }

# Fault endpoints
@app.post("/api/faults", status_code=201)
async def report_fault(fault: FaultData):
    """Report a vehicle fault"""
    fault_dict = fault.model_dump()
    fault_store.append(fault_dict)
    
    return {
        "message": "Fault reported",
        "fault_code": fault_dict['fault_code'],
        "severity": fault_dict['severity']
    }

@app.get("/api/faults")
async def get_faults(severity: Optional[str] = None, limit: int = 50):
    """Get reported faults"""
    results = fault_store.copy()
    
    if severity:
        results = [f for f in results if f.get('severity') == severity]
    
    results = results[:limit]
    
    return {
        "count": len(results),
        "data": results
    }

# Test endpoint
@app.get("/api/test")
async def test():
    return {
        "message": "API is working!",
        "timestamp": datetime.now().isoformat(),
        "storage": {
            "telemetry_records": len(telemetry_store),
            "fault_records": len(fault_store)
        }
    }

# Clear storage (for testing)
@app.post("/api/clear")
async def clear_storage():
    telemetry_store.clear()
    fault_store.clear()
    return {"message": "Storage cleared", "records": 0}

if __name__ == "__main__":
    print("🚗 Starting CarSafe API with in-memory storage...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)