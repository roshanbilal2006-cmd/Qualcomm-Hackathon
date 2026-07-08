# Setup Guide for LandSense AI Backend

This guide details running LandSense AI on a Snapdragon X Elite AI PC or local system (Windows ARM64 / x64).

## Prerequisites
- Python 3.12 (ARM64 or x64 equivalent)
- Git

## Installation

1. Navigate to the project folder:
   ```bash
   cd LandSense
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Spin up all simulated microservices and the backend server:
   ```bash
   python scripts/run_all.py
   ```

   This will:
   - Start the main Backend orchestrator on port `8000`.
   - Start the AI Model Service emulator on port `8001`.
   - Start the IoT Arduino Sensor emulator on port `8002`.
   - Start the Cloud Layer Sync emulator on port `8003`.
   - Start the MCP Services server on port `8004`.
   - Seed the local database with dummy RERA projects.
   - Serve the premium Web Dashboard locally.
