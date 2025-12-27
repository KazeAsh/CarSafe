from kafka_client import KafkaProducer
import json
import time
from datetime import datetime
from typing import Dict, Any
import logging

from src.data_generator.can_bus_simulator import FleetSimulator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VehicleDataProducer:
    """Kafka producer for vehicle telemetry data"""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None
        self.fleet_simulator = FleetSimulator(fleet_size=5)
        
    def connect(self):
        """Establish connection to Kafka"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                acks='all',
                retries=3
            )
            logger.info(f"Connected to Kafka at {self.bootstrap_servers}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
    
    def send_telemetry(self, topic: str = 'vehicle-telemetry'):
        """Send vehicle telemetry data to Kafka"""
        if not self.producer:
            self.connect()
            
        try:
            # Generate fleet data
            fleet_data = self.fleet_simulator.generate_fleet_data()
            
            for data in fleet_data:
                # Determine topic based on data type
                if 'fault' in data:
                    target_topic = 'vehicle-faults'
                else:
                    target_topic = topic
                
                # Send to Kafka
                future = self.producer.send(
                    target_topic,
                    value=data,
                    key=data['vehicle_id'].encode('utf-8')
                )
                
                # Optional: get result (for debugging)
                # record_metadata = future.get(timeout=10)
                # logger.debug(f"Sent to {record_metadata.topic}[{record_metadata.partition}]")
            
            self.producer.flush()
            logger.info(f"Sent {len(fleet_data)} messages to Kafka")
            return len(fleet_data)
            
        except Exception as e:
            logger.error(f"Error sending to Kafka: {e}")
            return 0
    
    def run_continuous(self, interval_seconds: float = 1.0):
        """Run producer continuously"""
        logger.info("Starting continuous data production...")
        try:
            while True:
                messages_sent = self.send_telemetry()
                logger.debug(f"Produced {messages_sent} messages")
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            logger.info("Stopping producer...")
            self.close()
    
    def close(self):
        """Close producer connection"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")


if __name__ == "__main__":
    # Test the producer
    producer = VehicleDataProducer()
    
    if producer.connect():
        # Send one batch for testing
        producer.send_telemetry()
        
        # Or run continuously (comment out for testing)
        # producer.run_continuous(interval_seconds=0.5)
        
        producer.close()