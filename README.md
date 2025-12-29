# 🚗 CarSafe - Vehicle Telemetry Monitoring System
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![Kafka](https://img.shields.io/badge/Kafka-Streaming-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A real-time vehicle telemetry pipeline featuring anomaly detection, live dashboards, and scalable event streaming — powered by FastAPI, Kafka, PostgreSQL, and Streamlit.



## 📸 Demo

*(Add a screenshot or GIF of your dashboard here)*  


## 📋 Features

- **Real-time telemetry ingestion** from simulated vehicles
- **Fault detection and reporting** with severity levels
- **RESTful API** with automatic OpenAPI documentation
- **Interactive dashboard** for real-time monitoring
- **Anomaly detection** for identifying unusual patterns
- **Kafka integration** for scalable data streaming

## 🏗️ CarSafe Architecture

<pre>
                          
+---------------------+     +-------------------+     +----------------------+
|   Data Generator    | --> |    FastAPI API    | --> |    PostgreSQL DB     |
|     (Simulation)    |     | (Telemetry Ingest)|     |    (Data Storage)    |
+---------------------+     +-------------------+     +----------------------+
            |                        |                          |
            |                        |                          |
            v                        v                          v
+---------------------+     +-------------------+     +----------------------+
|     Streamlit       |     |       Kafka       |     |   Anomaly Detection  |
|     Dashboard       |     |     (Optional)    |     |   (Pattern Analysis) |
+---------------------+     +-------------------+     +----------------------+
</pre>




## 🚀 Quick Start

### 🧰 Prerequisites
- Python 3.8+
- pip or Poetry
- PostgreSQL (optional for demo mode)
- Kafka (optional, only required for streaming mode)


## Installation

**Clone and setup:**
```bash
cd CarSafe
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```
## ▶️ Running the Services

### Start the API
```bash
uvicorn api.main:app --reload
python generator/main.py (Start the Data Generator)
streamlit run dashboard/app.py (Start the Dashboard)
```
## 🔌 API Documentation

Once the API is running:

- Swagger UI → http://localhost:8000/docs  
- ReDoc → http://localhost:8000/redoc  

## 🐳 Docker (Optional)

```bash
docker-compose up --build

