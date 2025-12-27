"""Basic tests for CarSafe"""
import pytest
import sys
import os
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_generator.can_bus_simulator import CANBusSimulator
from anomaly_detection.detector import AnomalyDetector


def test_can_bus_simulator_initialization():
    """Test CAN bus simulator initialization"""
    simulator = CANBusSimulator(vehicle_id="TEST001", make="Toyota", model="Camry")
    assert simulator.vehicle_id == "TEST001"
    assert simulator.make == "Toyota"
    assert simulator.model == "Camry"


def test_telemetry_generation():
    """Test telemetry data generation"""
    simulator = CANBusSimulator("TEST001")
    telemetry = simulator.generate_telemetry()
    
    assert isinstance(telemetry, dict)
    assert 'vehicle_id' in telemetry
    assert 'telemetry' in telemetry
    assert 'speed' in telemetry['telemetry']
    assert 0 <= telemetry['telemetry']['speed'] <= 300


def test_anomaly_detector_initialization():
    """Test anomaly detector initialization"""
    detector = AnomalyDetector(contamination=0.1)
    assert detector.contamination == 0.1
    assert detector.model is not None


def test_rule_based_anomaly_detection():
    """Test rule-based anomaly detection"""
    detector = AnomalyDetector()
    
    # Test normal data
    normal_data = {
        'vehicle_id': 'TEST001',
        'telemetry': {
            'speed': 60.0,
            'rpm': 2000,
            'brake': 0.0,
            'engine_temp': 90.0,
            'timestamp': datetime.now()
        }
    }
    
    result = detector.rule_based_detection(normal_data)
    assert isinstance(result, dict)
    assert 'is_anomaly' in result
    
    # Test anomaly data (sudden braking)
    anomaly_data = {
        'vehicle_id': 'TEST001',
        'telemetry': {
            'speed': 80.0,
            'rpm': 3000,
            'brake': 85.0,  # High brake pressure
            'engine_temp': 95.0,
            'timestamp': datetime.now()
        }
    }
    
    result = detector.rule_based_detection(anomaly_data)
    assert result['is_anomaly'] is True
    assert len(result['anomalies']) > 0


@pytest.mark.asyncio
async def test_api_health_check():
    """Test API health check endpoint"""
    # This would test the actual API endpoint
    # For now, just a placeholder
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])