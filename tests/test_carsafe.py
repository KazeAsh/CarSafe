# test_carsafe.py
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    print("🧪 Testing CarSafe API Endpoints")
    print("="*50)
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/health", "Health check"),
        ("GET", "/api/telemetry", "Get telemetry"),
        ("GET", "/api/faults", "Get faults"),
        ("GET", "/api/vehicles", "Get vehicles"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            elif method == "POST":
                response = requests.post(f"{BASE_URL}{endpoint}", timeout=5)
            
            print(f"{method} {endpoint}:")
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                print(f"  ✓ {description}")
                # Print a sample of the response
                data = response.json()
                if isinstance(data, dict) and "count" in data:
                    print(f"  Count: {data['count']}")
                elif isinstance(data, list):
                    print(f"  Items: {len(data)}")
            else:
                print(f"  ✗ Failed: {response.text[:100]}")
                
        except Exception as e:
            print(f"{method} {endpoint}: ✗ Error - {e}")
        
        print()
    
    # Test POST endpoints with sample data
    print("Testing POST endpoints:")
    print("-"*30)
    
    # Test telemetry endpoint
    telemetry_data = {
        "vehicle_id": "TEST001",
        "timestamp": datetime.now().isoformat(),
        "speed": 65.5,
        "rpm": 2500,
        "throttle": 35.0,
        "brake": 0.0,
        "engine_temp": 92.5,
        "fuel_level": 78.0,
        "latitude": 35.6895,
        "longitude": 139.6917,
        "odometer": 12345.6
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/telemetry", 
                               json=telemetry_data, timeout=5)
        print(f"POST /api/telemetry: {response.status_code}")
        if response.status_code == 201:
            print(f"  ✓ Telemetry sent successfully")
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"POST /api/telemetry: ✗ Error - {e}")
    
    print()
    
    # Test fault endpoint
    fault_data = {
        "vehicle_id": "TEST001",
        "timestamp": datetime.now().isoformat(),
        "fault_code": "P0300",
        "fault_description": "Test fault - Cylinder Misfire",
        "severity": "MEDIUM"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/faults", 
                               json=fault_data, timeout=5)
        print(f"POST /api/faults: {response.status_code}")
        if response.status_code == 201:
            print(f"  ✓ Fault reported successfully")
            print(f"  Response: {response.json()}")
    except Exception as e:
        print(f"POST /api/faults: ✗ Error - {e}")
    
    print("="*50)
    print("✅ Testing complete!")

if __name__ == "__main__":
    test_all_endpoints()