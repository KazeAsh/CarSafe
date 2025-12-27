# src/kafka_client/consumer.py
import logging

logger = logging.getLogger(__name__)

class VehicleDataConsumer:
    """Kafka consumer for vehicle telemetry data"""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        logger.info(f"VehicleDataConsumer initialized for {bootstrap_servers}")