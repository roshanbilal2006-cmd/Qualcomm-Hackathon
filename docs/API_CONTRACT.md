# API Contracts Specification

This document details all API contracts between LandSense subsystems.

## 1. Android → Backend
The Android app posts local site observations to the Backend.

### POST `/observation`
* **Request Payload**:
  ```json
  {
    "timestamp": "2026-07-08T09:40:00Z",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "images": ["base64_image_data_here..."],
    "voice_query": "Is this project legal?"
  }
  ```
* **Response Payload**: Universal Data Object (fused Observation JSON).

---

## 2. Backend → AI Service (FastVLM)
Visual reasoning service running on Snapdragon X Elite NPU.

### POST `/predict`
* **Request Payload**:
  ```json
  {
    "images": ["base64_image_data_here..."]
  }
  ```
* **Response Payload**:
  ```json
  {
    "stage": "Structure",
    "progress": 65.0,
    "confidence": 0.92,
    "description": "Concrete frame structure complete. Brickwork currently in progress.",
    "embedding": [0.015, -0.024, 0.187]
  }
  ```

---

## 3. Backend → IoT Service (Arduino UNO Q)
Local environmental telemetry.

### GET `/sensor`
* **Response Payload**:
  ```json
  {
    "noise_db": 74.2,
    "pm25": 38.5,
    "pm10": 79.1,
    "timestamp": "2026-07-08T09:40:05Z",
    "device_id": "ARDUINO_UNO_Q_01"
  }
  ```

---

## 4. Backend → MCP Service
RERA permits and tender details.

### GET `/nearby_projects`
* **Query Parameters**: `latitude`, `longitude`, `radius_meters`
* **Response Payload**:
  ```json
  [
    {
      "name": "Prestige Kings County",
      "builder": "Prestige Group",
      "status": "Approved",
      "distance": 120.5
    }
  ]
  ```

---

## 5. Backend → Cloud Service (Qualcomm AI Cloud 100)
Synchronizes the local observation to the global real-time heatmap.

### POST `/observation`
* **Request Payload**: Processed Observation JSON (strictly NO raw images/audio).
* **Response Payload**: `{ "sync_status": "success", "global_id": "cloud_obs_..." }`

### GET `/heatmap`
* **Response Payload**: List of coordinate bounds and construction scores for drawing visual heatmaps.

### GET `/history`
* **Response Payload**: Global observation log feed.
