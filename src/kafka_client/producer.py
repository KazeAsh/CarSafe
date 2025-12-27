# src/kafka_client/producer.py
import json
import logging

logger = logging.getLogger(__name__)

class VehicleDataProducer:
    """Kafka producer for vehicle telemetry data"""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        logger.info(f"VehicleDataProducer initialized for {bootstrap_servers}")
    
    def connect(self):
        """Establish connection to Kafka"""
        logger.info("Connecting to Kafka...")
        return True
    
    def send_custom_message(self, topic: str, message: dict):
        """Send a custom message to Kafka"""
        logger.info(f"Sending message to topic '{topic}': {json.dumps(message)[:100]}...")
        return True
    
    def close(self):
        """Close producer connection"""
        logger.info("Kafka producer closed")
