from kafka import KafkaConsumer
import json
import logging
from typing import Dict, Any, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VehicleDataConsumer:
    """Kafka consumer for vehicle telemetry data"""
    
    def __init__(self, bootstrap_servers: str = 'localhost:9092'):
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        self.running = False
        
    def connect(self, topics: List[str] = ['vehicle-telemetry', 'vehicle-faults']):
        """Connect to Kafka and subscribe to topics"""
        try:
            self.consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda v: json.loads(v.decode('utf-8')),
                key_deserializer=lambda v: v.decode('utf-8') if v else None,
                group_id='vehicle-data-processor',
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                max_poll_records=100
            )
            logger.info(f"Connected to Kafka and subscribed to {topics}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            return False
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process individual Kafka message"""
        processed = {
            'original': message,
            'processed_at': datetime.now().isoformat(),
            'checks': {}
        }
        
        # Basic data validation
        if 'vehicle_id' not in message:
            processed['checks']['has_vehicle_id'] = False
            processed['checks']['is_valid'] = False
        else:
            processed['checks']['has_vehicle_id'] = True
            
            # Check for required telemetry fields
            if 'telemetry' in message:
                telemetry = message['telemetry']
                processed['checks']['has_speed'] = 'speed' in telemetry
                processed['checks']['has_rpm'] = 'rpm' in telemetry
                processed['checks']['is_valid'] = True
            elif 'fault' in message:
                processed['checks']['is_fault'] = True
                processed['checks']['fault_code'] = message['fault'].get('code')
                processed['checks']['is_valid'] = True
            else:
                processed['checks']['is_valid'] = False
        
        return processed
    
    def consume(self, max_messages: int = None):
        """Consume messages from Kafka"""
        if not self.consumer:
            self.connect()
            
        self.running = True
        message_count = 0
        
        try:
            for message in self.consumer:
                if not self.running:
                    break
                    
                try:
                    # Process the message
                    processed = self.process_message(message.value)
                    
                    # Log based on message type
                    if 'fault' in message.value:
                        fault_code = message.value['fault']['code']
                        logger.warning(f"FAULT DETECTED: {fault_code} from {message.key}")
                    else:
                        speed = message.value.get('telemetry', {}).get('speed', 0)
                        logger.info(f"Telemetry: {message.key} - Speed: {speed:.1f} km/h")
                    
                    # Business logic would go here:
                    # - Store in database
                    # - Send to real-time analytics
                    # - Trigger alerts
                    
                    message_count += 1
                    if max_messages and message_count >= max_messages:
                        logger.info(f"Reached max messages ({max_messages})")
                        break
                        
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    
        except KeyboardInterrupt:
            logger.info("Consumer interrupted by user")
        finally:
            self.close()
    
    def consume_batch(self, batch_size: int = 10, timeout_ms: int = 1000):
        """Consume messages in batches"""
        if not self.consumer:
            self.connect()
            
        try:
            batch = self.consumer.poll(timeout_ms=batch_size * timeout_ms)
            
            for topic_partition, messages in batch.items():
                logger.info(f"Received {len(messages)} messages from {topic_partition}")
                
                for message in messages:
                    processed = self.process_message(message.value)
                    yield processed
                    
        except Exception as e:
            logger.error(f"Error in batch consumption: {e}")
    
    def close(self):
        """Close consumer connection"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")


if __name__ == "__main__":
    # Test the consumer
    consumer = VehicleDataConsumer()
    
    if consumer.connect():
        # Consume 5 messages for testing
        print("Consuming 5 messages...")
        
        for i, processed_msg in enumerate(consumer.consume_batch(batch_size=5)):
            print(f"Message {i+1}: {json.dumps(processed_msg, indent=2, default=str)}")
        
        # Or run continuously (comment out for testing)
        # consumer.consume()
        
        consumer.close()