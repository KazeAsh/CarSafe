# src/api/main.py - FIXED FOR PYDANTIC 2.5
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime, timedelta
import uvicorn
import json
import sys
import os

# Add parent directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now try imports with fallbacks
try:
    # Try absolute imports first
    from src.database.setup import DatabaseManager
    from src.kafka_client.producer import VehicleDataProducer
    from src.kafka_client.consumer import VehicleDataConsumer
    from src.anomaly_detection.detector import AnomalyDetector
except ImportError:
    try:
        # Try relative imports as fallback
        from database.setup import DatabaseManager
        from kafka_client.producer import VehicleDataProducer
        from kafka_client.consumer import VehicleDataConsumer
        from anomaly_detection.detector import AnomalyDetector
    except ImportError:
        # Create dummy classes if all imports fail
        print("⚠️ Warning: Could not import modules, using dummy implementations")
        
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
            def send_custom_message(self, topic, message): return True
        
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

# Pydantic Models - FIXED FOR PYDANTIC 2.5
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
    severity: Literal["LOW", "MEDIUM", "HIGH"]  # FIXED: Using Literal instead of regex
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        if v not in ["LOW", "MEDIUM", "HIGH"]:
            raise ValueError('Severity must be LOW, MEDIUM, or HIGH')
        return v

class VehicleInfo(BaseModel):
    vehicle_id: str
    make: str
    model: str
    year: Optional[int] = None

class AnomalyDetectionRequest(BaseModel):
    vehicle_id: str
    start_time: datetime
    end_time: datetime
    detection_type: str = "all"

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    db.connect()
    db.setup_tables()
    print("✅ CarSafe API started")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    db.close()
    print("🔌 CarSafe API shutdown")

# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "CarSafe API",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "api": "healthy",
            "database": "connected" if db.connect() else "disconnected"
        }
    }

# Telemetry endpoints
@app.post("/api/telemetry", status_code=201)
async def ingest_telemetry(telemetry: TelemetryData, background_tasks: BackgroundTasks):
    """Ingest vehicle telemetry data"""
    try:
        telemetry_dict = telemetry.model_dump()
        
        # Store in database
        db.insert_telemetry({
            'vehicle_id': telemetry_dict['vehicle_id'],
            'telemetry': telemetry_dict
        })
        
        # Send to Kafka
        background_tasks.add_task(
            kafka_producer.send_custom_message,
            topic="vehicle-telemetry",
            message=telemetry_dict
        )
        
        # Run anomaly detection
        background_tasks.add_task(
            anomaly_detector.detect_single_point,
            telemetry_dict
        )
        
        return {
            "message": "Telemetry ingested successfully",
            "vehicle_id": telemetry_dict['vehicle_id'],
            "timestamp": telemetry_dict['timestamp']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/telemetry")
async def get_telemetry(
    vehicle_id: Optional[str] = Query(None, description="Filter by vehicle ID"),
    start_time: Optional[datetime] = Query(None, description="Start time for filtering"),
    end_time: Optional[datetime] = Query(None, description="End time for filtering"),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get telemetry data with optional filters"""
    try:
        results = db.get_recent_telemetry(vehicle_id, limit)
        
        return {
            "count": len(results),
            "vehicle_id": vehicle_id,
            "data": results if results else []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/telemetry/stats")
async def get_telemetry_stats(
    vehicle_id: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168)
):
    """Get statistics for telemetry data"""
    return {
        "vehicle_id": vehicle_id or "all",
        "time_period_hours": hours,
        "stats": {
            "avg_speed": 65.5,
            "max_speed": 120.0,
            "avg_rpm": 2450,
            "max_rpm": 4500,
            "avg_engine_temp": 92.5,
            "data_points": 1250
        },
        "generated_at": datetime.now().isoformat()
    }

# Fault endpoints
@app.post("/api/faults", status_code=201)
async def report_fault(fault: FaultData, background_tasks: BackgroundTasks):
    """Report a vehicle fault"""
    try:
        fault_dict = fault.model_dump()
        
        # Store in database
        db.insert_fault(fault_dict)
        
        # Send to Kafka
        background_tasks.add_task(
            kafka_producer.send_custom_message,
            topic="vehicle-faults",
            message=fault_dict
        )
        
        return {
            "message": "Fault reported successfully",
            "fault_code": fault_dict['fault_code'],
            "severity": fault_dict['severity']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/faults")
async def get_faults(
    severity: Optional[str] = Query(None, pattern="^(LOW|MEDIUM|HIGH)$"),  # FIXED: pattern instead of regex
    resolved: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=500)
):
    """Get reported faults"""
    # Mock implementation - would query database in real app
    mock_faults = [
        {
            "vehicle_id": "VH0001",
            "timestamp": datetime.now().isoformat(),
            "fault_code": "P0300",
            "fault_description": "Random/Multiple Cylinder Misfire Detected",
            "severity": "HIGH",
            "resolved": False
        },
        {
            "vehicle_id": "VH0002",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
            "fault_code": "P0420",
            "fault_description": "Catalyst System Efficiency Below Threshold",
            "severity": "MEDIUM",
            "resolved": True
        }
    ]
    
    # Apply filters (mock)
    filtered = mock_faults
    if severity:
        filtered = [f for f in filtered if f['severity'] == severity]
    if resolved is not None:
        filtered = [f for f in filtered if f['resolved'] == resolved]
    
    return {
        "count": len(filtered),
        "filters": {"severity": severity, "resolved": resolved},
        "data": filtered[:limit]
    }

# Anomaly detection endpoints
@app.post("/api/anomalies/detect")
async def detect_anomalies(request: AnomalyDetectionRequest):
    """Trigger anomaly detection on historical data"""
    try:
        # This would trigger batch anomaly detection
        anomalies = anomaly_detector.detect_batch(
            vehicle_id=request.vehicle_id,
            start_time=request.start_time,
            end_time=request.end_time
        )
        
        return {
            "message": "Anomaly detection completed",
            "vehicle_id": request.vehicle_id,
            "period": {
                "start": request.start_time.isoformat(),
                "end": request.end_time.isoformat()
            },
            "anomalies_found": len(anomalies),
            "anomalies": anomalies[:10]  # Limit response size
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/anomalies")
async def get_anomalies(
    vehicle_id: Optional[str] = None,
    anomaly_type: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100)
):
    """Get detected anomalies"""
    # Mock implementation
    mock_anomalies = [
        {
            "vehicle_id": "VH0001",
            "timestamp": datetime.now().isoformat(),
            "anomaly_type": "sudden_deceleration",
            "description": "Sudden braking detected",
            "confidence": 0.92,
            "telemetry_snapshot": {
                "speed": 85.5,
                "brake": 95.0,
                "throttle": 5.0
            }
        }
    ]
    
    return {
        "count": len(mock_anomalies),
        "data": mock_anomalies
    }

# Vehicle management endpoints
@app.get("/api/vehicles")
async def get_vehicles():
    """Get list of registered vehicles"""
    # Mock implementation
    vehicles = [
        {"vehicle_id": "VH0001", "make": "Toyota", "model": "Camry", "year": 2022},
        {"vehicle_id": "VH0002", "make": "Toyota", "model": "Prius", "year": 2023},
        {"vehicle_id": "VH0003", "make": "Lexus", "model": "RX", "year": 2021}
    ]
    
    return {
        "count": len(vehicles),
        "data": vehicles
    }

@app.post("/api/vehicles", status_code=201)
async def register_vehicle(vehicle: VehicleInfo):
    """Register a new vehicle"""
    try:
        # In real implementation, would insert into vehicles table
        vehicle_dict = vehicle.model_dump()
        
        return {
            "message": "Vehicle registered successfully",
            "vehicle": vehicle_dict
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Data pipeline control endpoints
@app.post("/api/pipeline/start")
async def start_data_pipeline():
    """Start the data pipeline (producer/consumer)"""
    try:
        # In real implementation, would start background workers
        return {
            "message": "Data pipeline started",
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline/stop")
async def stop_data_pipeline():
    """Stop the data pipeline"""
    try:
        return {
            "message": "Data pipeline stopped",
            "status": "stopped",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple test endpoint
@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "CarSafe API is working!",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "/docs - API documentation",
            "/health - Health check",
            "/api/telemetry - Telemetry data",
            "/api/test - This test endpoint"
        ]
    }

if __name__ == "__main__":
    print("🚗 Starting CarSafe API...")
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )