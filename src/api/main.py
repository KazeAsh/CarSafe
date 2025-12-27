from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import json

from src.database.setup import DatabaseManager
from src.kafka_client.producer import VehicleDataProducer
from src.kafka_client.consumer import VehicleDataConsumer
from src.anomaly_detection.detector import AnomalyDetector

# Initialize FastAPI app
app = FastAPI(
    title="Vehicle Data Pipeline API",
    description="API for ingesting and querying vehicle telemetry data",
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
    severity: str = Field(..., regex="^(LOW|MEDIUM|HIGH)$")


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
    print("API started and database initialized")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    db.close()
    print("API shutdown complete")


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "service": "Vehicle Data Pipeline API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "telemetry": "/api/telemetry",
            "faults": "/api/faults",
            "vehicles": "/api/vehicles",
            "anomalies": "/api/anomalies",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_status = "healthy" if db.connect() else "unhealthy"
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "database": db_status,
            "api": "healthy"
        }
    }


# Telemetry endpoints
@app.post("/api/telemetry", status_code=201)
async def ingest_telemetry(telemetry: TelemetryData, background_tasks: BackgroundTasks):
    """Ingest vehicle telemetry data"""
    try:
        # Convert to dict for processing
        telemetry_dict = telemetry.dict()
        
        # Store in database
        db.insert_telemetry({
            'vehicle_id': telemetry_dict['vehicle_id'],
            'telemetry': telemetry_dict
        })
        
        # Send to Kafka for real-time processing
        background_tasks.add_task(
            kafka_producer.send_custom_message,
            topic="vehicle-telemetry",
            message=telemetry_dict
        )
        
        # Run anomaly detection in background
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
        # This would be expanded to use time filters
        results = db.get_recent_telemetry(vehicle_id, limit)
        
        if not results:
            return {"message": "No telemetry data found", "data": []}
        
        return {
            "count": len(results),
            "vehicle_id": vehicle_id,
            "data": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/telemetry/stats")
async def get_telemetry_stats(
    vehicle_id: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168)
):
    """Get statistics for telemetry data"""
    try:
        # In a real implementation, this would query aggregated stats
        # For demo, return mock statistics
        
        stats = {
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
        
        return stats
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Fault endpoints
@app.post("/api/faults", status_code=201)
async def report_fault(fault: FaultData, background_tasks: BackgroundTasks):
    """Report a vehicle fault"""
    try:
        fault_dict = fault.dict()
        
        # Store in database
        db.insert_fault(fault_dict)
        
        # Send to Kafka
        background_tasks.add_task(
            kafka_producer.send_custom_message,
            topic="vehicle-faults",
            message=fault_dict
        )
        
        # TODO: Trigger alert/notification
        
        return {
            "message": "Fault reported successfully",
            "fault_code": fault_dict['fault_code'],
            "severity": fault_dict['severity']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/faults")
async def get_faults(
    severity: Optional[str] = Query(None, regex="^(LOW|MEDIUM|HIGH)$"),
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
        vehicle_dict = vehicle.dict()
        
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


if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )