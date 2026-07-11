# Demo Walkthrough Guide

This document describes how to execute and verify the end-to-end LandSense AI pipeline.

## Demo Walkthrough Steps

### 1. Launch the Services
Start all servers by executing:
```bash
python scripts/run_all.py
```
Ensure all ports (8000, 8001, 8002, 8003, 8004) start listening successfully.

### 2. Open the Web Dashboard
Browse to `web/index.html` (or access the HTTP page served by Python) to see the empty construction activity heatmap and observation logs.

### 3. Simulate a Capture from OnePlus 15
Run the simulation script:
```bash
python scripts/simulate_scan.py
```

This simulates a user pointing their OnePlus 15 camera at a construction site in Whitefield, Bangalore, capturing GPS details, and sending it to the backend.

### 4. Verify the Fusion and Correlation Pipeline
Observe the console logs in the Backend terminal:
- **Step 1**: Receives Phone Scan request at `POST /observation`.
- **Step 2**: Triggers FastVLM model via `POST /predict` (running on Port 8001).
- **Step 3**: Queries Arduino Uno Q sensor node via `GET /sensor` (running on Port 8002).
- **Step 4**: Runs the correlation engine. If the sensor timestamp is within 30 seconds and distance is within 50 meters, sensor records are fused.
- **Step 5**: Queries local SQLite DB (simulating RERA records) for builders within 500m.
- **Step 6**: Development score is calculated based on noise level, dust density, construction stage, and RERA approval status.
- **Step 7**: Fused Observation object is synchronized to Qualcomm AI Cloud 100 via `POST /observation` (running on Port 8003).
- **Step 8**: Heatmap and History datasets are updated dynamically.

### 5. View Real-time Heatmap
Refresh the Web Dashboard. You will see:
- A new active indicator pin at the simulated GPS coordinates (Whitefield).
- An explainable construction report outlining:
  - Estimated Construction Stage & Progress %
  - Current Noise (dB) and Dust (PM2.5/PM10) readings
  - Linked RERA Permits
  - Overall Development Score with clean explanatory warnings.
