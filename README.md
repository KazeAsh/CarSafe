# 🚗 CarSafe - Vehicle Telemetry Monitoring System

A real-time vehicle data pipeline with anomaly detection, built with FastAPI, Kafka, and Streamlit.

## 📋 Features

- **Real-time telemetry ingestion** from simulated vehicles
- **Fault detection and reporting** with severity levels
- **RESTful API** with automatic OpenAPI documentation
- **Interactive dashboard** for real-time monitoring
- **Anomaly detection** for identifying unusual patterns
- **Kafka integration** for scalable data streaming

## 🏗️ CarSafe Architecture

 ┌────────────────────┐        ┌──────────────────┐        ┌────────────────────┐
 │   Data Generator   │  --->  │    FastAPI API   │  --->  │    PostgreSQL DB    │
 │   (Simulation)     │        │ (Telemetry Ingest)│       │   (Data Storage)    │
 └────────────────────┘        └──────────────────┘        └────────────────────┘
            │                          │                           │
            │                          │                           │
            ▼                          ▼                           ▼
 ┌────────────────────┐        ┌──────────────────┐        ┌────────────────────┐
 │   Streamlit         │        │      Kafka       │        │   Anomaly Detection │
 │   Dashboard         │        │   (Optional)     │        │ (Pattern Analysis)  │
 └────────────────────┘        └──────────────────┘        └────────────────────┘



## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL (optional for demo)

### Installation

1. **Clone and setup:**
```bash
cd CarSafe
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
