# src/data_generator/can_bus_simulator.py
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
