-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id VARCHAR(20) PRIMARY KEY,
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS telemetry (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
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
);

CREATE TABLE IF NOT EXISTS faults (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    vehicle_id VARCHAR(20) REFERENCES vehicles(vehicle_id),
    timestamp TIMESTAMP NOT NULL,
    fault_code VARCHAR(10),
    fault_description TEXT,
    severity VARCHAR(10) CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH')),
    resolved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS anomalies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    vehicle_id VARCHAR(20) REFERENCES vehicles(vehicle_id),
    timestamp TIMESTAMP NOT NULL,
    anomaly_type VARCHAR(50),
    description TEXT,
    confidence DECIMAL(5,4),
    telemetry_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_timestamp ON telemetry(vehicle_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_telemetry_timestamp ON telemetry(timestamp);
CREATE INDEX IF NOT EXISTS idx_faults_vehicle_timestamp ON faults(vehicle_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_faults_severity ON faults(severity);
CREATE INDEX IF NOT EXISTS idx_anomalies_vehicle_type ON anomalies(vehicle_id, anomaly_type);

-- Insert sample vehicles
INSERT INTO vehicles (vehicle_id, make, model, year) VALUES
('VH0001', 'Toyota', 'Camry', 2023),
('VH0002', 'Toyota', 'Prius', 2022),
('VH0003', 'Lexus', 'RX', 2023),
('VH0004', 'Toyota', 'RAV4', 2022),
('VH0005', 'Lexus', 'ES', 2023)
ON CONFLICT (vehicle_id) DO NOTHING;