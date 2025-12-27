# src/data_generator/main.py
import requests
import time
import random
from datetime import datetime
from .can_bus_simulator import CANBusSimulator

BASE_URL = "http://localhost:8000"

def generate_test_data():
    """Generate and send test data to the API"""
    
    # Create simulators for different vehicles
    vehicles = [
        CANBusSimulator("VH0001", "Toyota", "Camry"),
        CANBusSimulator("VH0002", "Toyota", "Prius"),
        CANBusSimulator("VH0003", "Lexus", "RX")
    ]
    
    print("🚗 Starting CarSafe data generator...")
    print(f"Sending data to: {BASE_URL}")
    
    counter = 0
    try:
        while True:
            for vehicle in vehicles:
                # Generate telemetry
                telemetry = vehicle.generate_telemetry()
                
                # Format for API
                telemetry_data = {
                    "vehicle_id": telemetry['vehicle_id'],
                    "timestamp": telemetry['telemetry']['timestamp'].isoformat(),
                    "speed": telemetry['telemetry']['speed'],
                    "rpm": telemetry['telemetry']['rpm'],
                    "throttle": telemetry['telemetry']['throttle'],
                    "brake": telemetry['telemetry']['brake'],
                    "engine_temp": telemetry['telemetry']['engine_temp'],
                    "fuel_level": telemetry['telemetry']['fuel_level'],
                    "latitude": telemetry['telemetry']['latitude'],
                    "longitude": telemetry['telemetry']['longitude'],
                    "odometer": telemetry['telemetry']['odometer']
                }
                
                # Send to API
                try:
                    response = requests.post(
                        f"{BASE_URL}/api/telemetry",
                        json=telemetry_data,
                        timeout=2
                    )
                    if response.status_code == 201:
                        print(f"✓ Sent telemetry: {vehicle.vehicle_id} - Speed: {telemetry_data['speed']:.1f} km/h")
                    else:
                        print(f"✗ Failed: {response.status_code}")
                except Exception as e:
                    print(f"✗ Connection error: {e}")
                
                # Occasionally generate a fault (5% chance)
                if random.random() < 0.05:
                    fault_codes = [
                        ("P0300", "Random/Multiple Cylinder Misfire Detected"),
                        ("P0420", "Catalyst System Efficiency Below Threshold"),
                        ("P0171", "System Too Lean (Bank 1)"),
                        ("P0442", "Evaporative Emission Control System Leak Detected")
                    ]
                    
                    fault_code, description = random.choice(fault_codes)
                    severity = random.choice(["LOW", "MEDIUM", "HIGH"])
                    
                    fault_data = {
                        "vehicle_id": vehicle.vehicle_id,
                        "timestamp": datetime.now().isoformat(),
                        "fault_code": fault_code,
                        "fault_description": description,
                        "severity": severity
                    }
                    
                    try:
                        response = requests.post(
                            f"{BASE_URL}/api/faults",
                            json=fault_data,
                            timeout=2
                        )
                        if response.status_code == 201:
                            print(f"⚠️ Reported fault: {fault_code} ({severity})")
                    except Exception as e:
                        print(f"✗ Fault reporting failed: {e}")
            
            counter += 1
            print(f"Batch {counter} complete. Waiting...")
            time.sleep(2)  # Send data every 2 seconds
            
    except KeyboardInterrupt:
        print("\n Data generator stopped")

if __name__ == "__main__":
    generate_test_data()