import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import logging
import json

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """Detects anomalies in vehicle telemetry data"""
    
    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        
    def prepare_features(self, telemetry_data: List[Dict]) -> np.ndarray:
        """Prepare features for anomaly detection"""
        features = []
        
        for data in telemetry_data:
            telemetry = data.get('telemetry', {})
            
            feature_vector = [
                telemetry.get('speed', 0),
                telemetry.get('rpm', 0),
                telemetry.get('throttle', 0),
                telemetry.get('brake', 0),
                telemetry.get('engine_temp', 0),
                telemetry.get('fuel_level', 0)
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def train(self, training_data: List[Dict]):
        """Train the anomaly detection model"""
        try:
            features = self.prepare_features(training_data)
            
            if len(features) < 10:
                logger.warning("Insufficient training data")
                return False
            
            # Scale features
            scaled_features = self.scaler.fit_transform(features)
            
            # Train model
            self.model.fit(scaled_features)
            self.is_trained = True
            
            logger.info(f"Anomaly detector trained on {len(features)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Error training anomaly detector: {e}")
            return False
    
    def detect_single_point(self, telemetry_data: Dict) -> Dict:
        """Detect anomalies in a single telemetry point"""
        if not self.is_trained:
            # Use simple rule-based detection if model not trained
            return self.rule_based_detection(telemetry_data)
        
        try:
            # Prepare features for single point
            features = self.prepare_features([telemetry_data])
            scaled_features = self.scaler.transform(features)
            
            # Predict anomaly
            prediction = self.model.predict(scaled_features)
            anomaly_score = self.model.score_samples(scaled_features)
            
            is_anomaly = prediction[0] == -1
            confidence = abs(anomaly_score[0])
            
            result = {
                'is_anomaly': bool(is_anomaly),
                'confidence': float(confidence),
                'anomaly_type': 'machine_learning',
                'telemetry': telemetry_data
            }
            
            # Add rule-based checks as well
            rule_based = self.rule_based_detection(telemetry_data)
            if rule_based['is_anomaly']:
                result['rule_based_anomalies'] = rule_based['anomalies']
                result['is_anomaly'] = True  # Override if rule-based says anomaly
            
            return result
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return {
                'is_anomaly': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def rule_based_detection(self, telemetry_data: Dict) -> Dict:
        """Rule-based anomaly detection"""
        anomalies = []
        telemetry = telemetry_data.get('telemetry', {})
        
        # Rule 1: Sudden braking
        if telemetry.get('brake', 0) > 80 and telemetry.get('speed', 0) > 60:
            anomalies.append({
                'type': 'sudden_braking',
                'severity': 'HIGH',
                'description': f"Sudden braking at {telemetry.get('speed')} km/h",
                'confidence': 0.9
            })
        
        # Rule 2: Engine overheating
        if telemetry.get('engine_temp', 0) > 105:
            anomalies.append({
                'type': 'engine_overheating',
                'severity': 'HIGH',
                'description': f"Engine temperature critical: {telemetry.get('engine_temp')}°C",
                'confidence': 0.95
            })
        
        # Rule 3: High RPM at low speed (potential engine strain)
        if telemetry.get('rpm', 0) > 3500 and telemetry.get('speed', 0) < 20:
            anomalies.append({
                'type': 'high_rpm_low_speed',
                'severity': 'MEDIUM',
                'description': f"High RPM ({telemetry.get('rpm')}) at low speed ({telemetry.get('speed')} km/h)",
                'confidence': 0.7
            })
        
        # Rule 4: Low fuel with high speed
        if telemetry.get('fuel_level', 0) < 15 and telemetry.get('speed', 0) > 80:
            anomalies.append({
                'type': 'low_fuel_high_speed',
                'severity': 'MEDIUM',
                'description': f"Low fuel ({telemetry.get('fuel_level')}%) at high speed",
                'confidence': 0.6
            })
        
        # Rule 5: Abnormal throttle-brake combination
        if telemetry.get('throttle', 0) > 30 and telemetry.get('brake', 0) > 30:
            anomalies.append({
                'type': 'conflicting_inputs',
                'severity': 'LOW',
                'description': "Both throttle and brake applied significantly",
                'confidence': 0.5
            })
        
        return {
            'is_anomaly': len(anomalies) > 0,
            'anomalies': anomalies,
            'telemetry': telemetry_data
        }
    
    def detect_batch(self, 
                    vehicle_id: str, 
                    start_time: datetime, 
                    end_time: datetime) -> List[Dict]:
        """Detect anomalies in a batch of historical data"""
        # In a real implementation, this would query the database
        # For now, return mock anomalies
        
        mock_anomalies = [
            {
                'vehicle_id': vehicle_id,
                'timestamp': start_time + timedelta(minutes=30),
                'anomaly_type': 'sudden_braking',
                'description': 'Sudden deceleration detected',
                'confidence': 0.92,
                'telemetry_snapshot': {
                    'speed': 85.5,
                    'brake': 95.0,
                    'throttle': 5.0
                }
            },
            {
                'vehicle_id': vehicle_id,
                'timestamp': start_time + timedelta(hours=1),
                'anomaly_type': 'engine_overheating',
                'description': 'Engine temperature exceeded safe limits',
                'confidence': 0.88,
                'telemetry_snapshot': {
                    'engine_temp': 108.5,
                    'speed': 75.0,
                    'rpm': 3200
                }
            }
        ]
        
        return mock_anomalies
    
    def generate_training_data(self, n_samples: int = 1000) -> List[Dict]:
        """Generate synthetic training data"""
        training_data = []
        
        for i in range(n_samples):
            telemetry = {
                'vehicle_id': f"TRAIN{i%10:03d}",
                'telemetry': {
                    'speed': np.random.uniform(0, 120),
                    'rpm': np.random.uniform(800, 4000),
                    'throttle': np.random.uniform(0, 100),
                    'brake': np.random.uniform(0, 100),
                    'engine_temp': np.random.uniform(85, 105),
                    'fuel_level': np.random.uniform(10, 100),
                    'timestamp': datetime.now()
                }
            }
            training_data.append(telemetry)
        
        # Add some anomalies to training data
        for i in range(int(n_samples * 0.05)):  # 5% anomalies
            telemetry = {
                'vehicle_id': f"TRAIN{i%10:03d}",
                'telemetry': {
                    'speed': np.random.uniform(100, 150),  # Too fast
                    'rpm': np.random.uniform(4000, 6000),  # Too high RPM
                    'throttle': 100,  # Max throttle
                    'brake': 100,  # Max brake
                    'engine_temp': np.random.uniform(110, 130),  # Overheating
                    'fuel_level': np.random.uniform(0, 5),  # Empty
                    'timestamp': datetime.now()
                }
            }
            training_data.append(telemetry)
        
        return training_data


if __name__ == "__main__":
    # Test the anomaly detector
    detector = AnomalyDetector()
    
    # Generate and train on synthetic data
    training_data = detector.generate_training_data(1000)
    detector.train(training_data)
    
    # Test detection on new data
    test_data = {
        'vehicle_id': 'TEST001',
        'telemetry': {
            'speed': 120.5,
            'rpm': 4500,
            'throttle': 85.0,
            'brake': 0.0,
            'engine_temp': 95.5,
            'fuel_level': 65.0,
            'timestamp': datetime.now()
        }
    }
    
    result = detector.detect_single_point(test_data)
    print("Anomaly Detection Result:")
    print(json.dumps(result, indent=2, default=str))