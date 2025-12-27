import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import numpy as np


class CANBusSimulator:
    """Simulates CAN bus data from vehicles"""
    
    def __init__(self, vehicle_id: str, make: str = "Toyota", model: str = "Camry"):
        self.vehicle_id = vehicle_id
        self.make = make
        self.model = model
        self.state = {
            'speed': 0.0,  # km/h
            'rpm': 800.0,  # RPM
            'throttle': 0.0,  # %
            'brake': 0.0,  # %
            'engine_temp': 90.0,  # °C
            'fuel_level': 80.0,  # %
            'odometer': random.randint(1000, 50000),
            'timestamp': datetime.now()
        }
        
    def generate_telemetry(self) -> Dict:
        """Generate realistic vehicle telemetry data"""
        # Simulate driving patterns
        if random.random() < 0.3:  # 30% chance of acceleration
            self.state['speed'] = min(self.state['speed'] + random.uniform(1, 5), 120)
            self.state['rpm'] = min(self.state['rpm'] + random.uniform(50, 200), 4000)
            self.state['throttle'] = min(self.state['throttle'] + random.uniform(5, 15), 100)
        elif random.random() < 0.2:  # 20% chance of braking
            self.state['speed'] = max(self.state['speed'] - random.uniform(2, 8), 0)
            self.state['rpm'] = max(self.state['rpm'] - random.uniform(50, 150), 800)
            self.state['brake'] = min(self.state['brake'] + random.uniform(10, 30), 100)
        else:  # 50% chance of cruising
            self.state['speed'] = max(0, self.state['speed'] + random.uniform(-1, 1))
            self.state['rpm'] = max(800, self.state['rpm'] + random.uniform(-20, 20))
            self.state['throttle'] = max(0, self.state['throttle'] + random.uniform(-2, 2))
            self.state['brake'] = max(0, self.state['brake'] + random.uniform(-5, 5))
        
        # Engine temperature simulation
        if self.state['speed'] > 60:
            self.state['engine_temp'] = min(self.state['engine_temp'] + random.uniform(0.1, 0.5), 110)
        else:
            self.state['engine_temp'] = max(80, self.state['engine_temp'] + random.uniform(-0.2, 0.2))
        
        # Fuel consumption
        fuel_consumption = 0.01 + (self.state['speed'] * 0.001) + (self.state['rpm'] * 0.00001)
        self.state['fuel_level'] = max(0, self.state['fuel_level'] - fuel_consumption)
        
        # Update timestamp
        self.state['timestamp'] = datetime.now()
        
        # Add some noise
        telemetry = self.state.copy()
        telemetry['speed'] += random.uniform(-0.5, 0.5)
        telemetry['rpm'] += random.uniform(-10, 10)
        
        # Add GPS-like data
        telemetry['latitude'] = 35.6895 + random.uniform(-0.01, 0.01)
        telemetry['longitude'] = 139.6917 + random.uniform(-0.01, 0.01)
        
        return {
            'vehicle_id': self.vehicle_id,
            'make': self.make,
            'model': self.model,
            'telemetry': telemetry,
            'metadata': {
                'data_type': 'can_bus',
                'version': '1.0',
                'sequence_id': int(time.time() * 1000)
            }
        }
    
    def generate_fault(self) -> Optional[Dict]:
        """Occasionally generate fault data (5% chance)"""
        if random.random() < 0.05:
            faults = [
                {'code': 'P0300', 'description': 'Random/Multiple Cylinder Misfire Detected'},
                {'code': 'P0420', 'description': 'Catalyst System Efficiency Below Threshold'},
                {'code': 'P0171', 'description': 'System Too Lean (Bank 1)'},
                {'code': 'P0442', 'description': 'Evaporative Emission Control System Leak Detected'},
                {'code': 'P0128', 'description': 'Coolant Thermostat (Coolant Temperature Below Thermostat Regulating Temperature)'}
            ]
            
            return {
                'vehicle_id': self.vehicle_id,
                'timestamp': datetime.now().isoformat(),
                'fault': random.choice(faults),
                'severity': random.choice(['LOW', 'MEDIUM', 'HIGH']),
                'metadata': {
                    'data_type': 'diagnostic',
                    'version': '1.0'
                }
            }
        return None


class FleetSimulator:
    """Simulates data from multiple vehicles"""
    
    def __init__(self, fleet_size: int = 10):
        self.vehicles = []
        makes_models = [
            ('Toyota', 'Camry'), ('Toyota', 'Prius'), ('Toyota', 'RAV4'),
            ('Lexus', 'RX'), ('Lexus', 'ES'), ('Subaru', 'Outback')
        ]
        
        for i in range(fleet_size):
            make, model = random.choice(makes_models)
            vehicle = CANBusSimulator(
                vehicle_id=f"VH{str(i+1).zfill(4)}",
                make=make,
                model=model
            )
            self.vehicles.append(vehicle)
    
    def generate_fleet_data(self) -> List[Dict]:
        """Generate data for entire fleet"""
        fleet_data = []
        for vehicle in self.vehicles:
            fleet_data.append(vehicle.generate_telemetry())
            
            # Occasionally add fault data
            fault = vehicle.generate_fault()
            if fault:
                fleet_data.append(fault)
        
        return fleet_data


if __name__ == "__main__":
    # Test the simulator
    fleet = FleetSimulator(3)
    for i in range(5):
        data = fleet.generate_fleet_data()
        print(f"Batch {i+1}: Generated {len(data)} messages")
        for msg in data[:2]:  # Print first 2 messages
            print(json.dumps(msg, default=str, indent=2))
        print("-" * 50)
        time.sleep(1)