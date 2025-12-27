import psycopg2
from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages PostgreSQL database setup and connections"""
    
    def __init__(self, 
                 host='localhost', 
                 port=5432, 
                 database='vehicledata',
                 user='admin', 
                 password='password'):
        self.connection_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.conn = None
        
    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(**self.connection_params)
            self.conn.autocommit = False
            logger.info("Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def setup_tables(self):
        """Create necessary tables"""
        tables_sql = {
            'vehicles': """
                CREATE TABLE IF NOT EXISTS vehicles (
                    vehicle_id VARCHAR(20) PRIMARY KEY,
                    make VARCHAR(50),
                    model VARCHAR(50),
                    year INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'telemetry': """
                CREATE TABLE IF NOT EXISTS telemetry (
                    id BIGSERIAL PRIMARY KEY,
                    vehicle_id VARCHAR(20) REFERENCES vehicles(vehicle_id),
                    timestamp TIMESTAMP NOT NULL,
                    speed DECIMAL(5,2),
                    rpm INTEGER,
                    throttle DECIMAL(5,2),
                    brake DECIMAL(5,2),
                    engine_temp DECIMAL(5,2),
                    fuel_level DECIMAL(5,2),
                    latitude DECIMAL(10,6),
                    longitude DECIMAL(10,6),
                    odometer DECIMAL(10,2),
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'faults': """
                CREATE TABLE IF NOT EXISTS faults (
                    id BIGSERIAL PRIMARY KEY,
                    vehicle_id VARCHAR(20) REFERENCES vehicles(vehicle_id),
                    timestamp TIMESTAMP NOT NULL,
                    fault_code VARCHAR(10),
                    fault_description TEXT,
                    severity VARCHAR(10),
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            'anomalies': """
                CREATE TABLE IF NOT EXISTS anomalies (
                    id BIGSERIAL PRIMARY KEY,
                    vehicle_id VARCHAR(20) REFERENCES vehicles(vehicle_id),
                    timestamp TIMESTAMP NOT NULL,
                    anomaly_type VARCHAR(50),
                    description TEXT,
                    confidence DECIMAL(5,4),
                    telemetry_data JSONB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
        }
        
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_timestamp ON telemetry(vehicle_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_faults_vehicle_timestamp ON faults(vehicle_id, timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_faults_severity ON faults(severity)",
            "CREATE INDEX IF NOT EXISTS idx_anomalies_vehicle_type ON anomalies(vehicle_id, anomaly_type)"
        ]
        
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        
        try:
            # Create tables
            for table_name, create_sql in tables_sql.items():
                cursor.execute(create_sql)
                logger.info(f"Created/verified table: {table_name}")
            
            # Create indexes
            for index_sql in indexes_sql:
                cursor.execute(index_sql)
            
            self.conn.commit()
            logger.info("Database schema created successfully")
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error creating schema: {e}")
            raise
        finally:
            cursor.close()
    
    def insert_telemetry(self, telemetry_data: dict):
        """Insert telemetry data into database"""
        insert_sql = """
            INSERT INTO telemetry 
            (vehicle_id, timestamp, speed, rpm, throttle, brake, 
             engine_temp, fuel_level, latitude, longitude, odometer)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor = self.conn.cursor()
        try:
            telemetry = telemetry_data['telemetry']
            cursor.execute(insert_sql, (
                telemetry_data['vehicle_id'],
                telemetry['timestamp'],
                telemetry.get('speed'),
                telemetry.get('rpm'),
                telemetry.get('throttle'),
                telemetry.get('brake'),
                telemetry.get('engine_temp'),
                telemetry.get('fuel_level'),
                telemetry.get('latitude'),
                telemetry.get('longitude'),
                telemetry.get('odometer')
            ))
            
            self.conn.commit()
            return cursor.rowcount
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting telemetry: {e}")
            return 0
        finally:
            cursor.close()
    
    def insert_fault(self, fault_data: dict):
        """Insert fault data into database"""
        insert_sql = """
            INSERT INTO faults 
            (vehicle_id, timestamp, fault_code, fault_description, severity)
            VALUES (%s, %s, %s, %s, %s)
        """
        
        cursor = self.conn.cursor()
        try:
            fault = fault_data['fault']
            cursor.execute(insert_sql, (
                fault_data['vehicle_id'],
                fault_data['timestamp'],
                fault['code'],
                fault['description'],
                fault_data['severity']
            ))
            
            self.conn.commit()
            return cursor.rowcount
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Error inserting fault: {e}")
            return 0
        finally:
            cursor.close()
    
    def get_recent_telemetry(self, vehicle_id: str = None, limit: int = 100):
        """Get recent telemetry data"""
        if vehicle_id:
            query = """
                SELECT * FROM telemetry 
                WHERE vehicle_id = %s 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            params = (vehicle_id, limit)
        else:
            query = """
                SELECT * FROM telemetry 
                ORDER BY timestamp DESC 
                LIMIT %s
            """
            params = (limit,)
        
        cursor = self.conn.cursor()
        try:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            logger.error(f"Error fetching telemetry: {e}")
            return []
        finally:
            cursor.close()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


if __name__ == "__main__":
    # Test database setup
    db = DatabaseManager()
    
    if db.connect():
        db.setup_tables()
        
        # Test data insertion
        test_telemetry = {
            'vehicle_id': 'VH0001',
            'telemetry': {
                'timestamp': '2024-01-15 10:30:00',
                'speed': 65.5,
                'rpm': 2500,
                'throttle': 35.5,
                'brake': 0.0,
                'engine_temp': 92.5,
                'fuel_level': 75.5,
                'latitude': 35.6895,
                'longitude': 139.6917,
                'odometer': 12345.6
            }
        }
        
        db.insert_telemetry(test_telemetry)
        
        # Fetch and display
        results = db.get_recent_telemetry(limit=5)
        print("Recent telemetry:", results)
        
        db.close()