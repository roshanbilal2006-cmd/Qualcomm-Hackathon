# LandSense AI: Current System Architecture Reverse-Engineering

**Document Version:** 1.0.0  
**Inspection Date:** 2026-10-07  
**Scope:** Complete repository audit across Mobile, AI, Backend Orchestrator, MCP (IoT/RERA), Cloud, and Web layers.

---

## 1. Current Inputs

The LandSense AI system in its current implementation accepts the following inputs across its microservices:

1. **Client / Mobile Ingestion (`POST /observation` to Backend):**
   - `images`: 1 to 4 images encoded as base64 or data URLs (`data:image/jpeg;base64,...`).
   - `latitude`: Mobile device GPS latitude (float, WGS84).
   - `longitude`: Mobile device GPS longitude (float, WGS84).
   - `timestamp`: ISO 8601 UTC timestamp string (e.g., `2026-07-09T10:30:00Z`).
   - `owner_id`: Optional client device/user UUID.
   - `voice_query`: Optional natural language query string or transcribed audio.
   - `noise_db`, `dust_pm25`, `dust_pm10`, `sensor_timestamp`: Optional client-supplied telemetry bypass fields.

2. **IoT Hardware / Serial Ingestion (`mcp/adapters/sensor/arduino_sensor_adapter.py`):**
   - Serial port stream (`COM3` on Windows, baud rate 9600).
   - Wire format: ASCII line containing three comma-separated float tokens: `noise_db,pm25,pm10` (e.g., `72.4,38.1,61.7`).
   - Generated internally by Arduino adapter: system timestamp (`datetime.now(timezone.utc)`), fixed `device_id="UNO-Q"`.

3. **Simulated / Demo Sensor Ingestion (`mcp/adapters/sensor/dummy_sensor_adapter.py`):**
   - Pseudo-random values drawn uniformly at query time:
     - `noise_db` $\sim \mathcal{U}(40.0, 90.0)$
     - `pm25` $\sim \mathcal{U}(10.0, 100.0)$
     - `pm10` $\sim \mathcal{U}(20.0, 150.0)$
   - Static coordinates: `latitude=12.9716, longitude=77.7500`.

4. **Regulatory / Planning Ingestion (`mcp/data/mock_rera.json`):**
   - Static local JSON dataset containing records with:
     - `name`: Project commercial identifier (e.g., "Prestige Kings County").
     - `builder`: Construction developer name.
     - `status`: Regulatory status string ("Approved", "Disputed", "Unauthorized", "Pending").
     - `latitude`, `longitude`: Fixed project centroids.
     - Static sample baseline telemetry: `noise_db`, `dust_pm25`, `dust_pm10`.

---

## 2. Current Processing

The end-to-end processing pipeline executes sequentially upon invocation of `ObservationPipeline.execute(input_data)`:

```
[Mobile/Client Request]
       │
       ▼
[Backend Orchestrator: ObservationPipeline.execute]
       │
       ├─► 1. AIAdapter -> AI Service (/predict)
       │         │
       │         ├─► Decodes base64 JPEG
       │         ├─► OpenCV heuristic feature extractor (HSV color ratios, Sobel/Canny edges, contours)
       │         ├─► Cloud VLM (Cirrascale LLaMA-3.3-70B) or local OpenCV rule-based fallback
       │         └─► Returns: stage, progress %, confidence, embedding (128-dim)
       │
       ├─► 2. MCPAdapter -> MCP Service (/sensor)
       │         │
       │         ├─► Queries live Arduino serial adapter or DummySensorAdapter
       │         └─► Returns: noise_db, pm25, pm10, timestamp, device_id
       │
       ├─► 3. Spatial & Temporal Correlation Engine (correlation.py)
       │         │
       │         ├─► Haversine distance between Phone GPS and Sensor GPS (threshold <= 50m)
       │         └─► Absolute time delta |Phone_ts - Sensor_ts| (threshold <= 30s)
       │
       ├─► 4. MCPAdapter -> MCP Service (/nearby_projects)
       │         │
       │         └─► Linear scan of mock_rera.json within Euclidean/Haversine radius <= 500m
       │
       ├─► 5. Scoring & Heuristic Fusion Engine (scoring.py)
       │         │
       │         └─► Arithmetic additive rule combining visual progress %, RERA penalty/bonus, and sensor delta
       │
       └─► 6. Persistence & Cloud Sync
                 ├─► Local SQLite database (backend.db via SQLAlchemy)
                 └─► HTTP POST to Cloud Community Layer (/observation -> cloud_data.db)
```

---

## 3. Current Outputs

1. **Observation Response (`ObservationResponse` Pydantic model):**
   - `observation_id`: Generated UUIDv4 string.
   - `construction_stage`: Classified discrete stage string (`"Not Started"`, `"Site Preparation"`, `"Foundation"`, `"Structural Work"`, `"Brickwork"`, `"Finishing"`, `"Completed"`, or `"Unknown"`).
   - `confidence`: Visual classifier confidence float $[0.0, 1.0]$.
   - `progress`: Estimated construction completion percentage float $[0.0, 100.0]$.
   - `noise_db`: Correlated acoustic sound pressure level (dBA) or `null`.
   - `dust_pm25`: Correlated fine particulate concentration ($\mu\text{g/m}^3$) or `null`.
   - `dust_pm10`: Correlated coarse particulate concentration ($\mu\text{g/m}^3$) or `null`.
   - `sensor_status`: Status label (`"connected"`, `"simulated"`, `"crowdsourced"`, `"degraded"`, `"disconnected"`).
   - `rera_projects`: List of matched projects within 500m with calculated distances.
   - `development_score`: Computed scalar index $[0.0, 100.0]$.
   - `summary`: String concatenating visual description, RERA status, and sensor delta warnings.
   - `risk`: Categorical risk classification (`"Low"`, `"Medium"`, `"High"`).

2. **Cloud & Public API Endpoints:**
   - `GET /heatmap`: Array of spatial coordinate tuples `(lat, lon, score, stage, dust, noise)`.
   - `GET /history`: Filtered temporal array of historical scans.
   - `POST /chat`: RAG-like string output answering questions using recent observation snippets and Cirrascale LLM.

---

## 4. Current Hardware

- **Teammate Hardware Node (IoT):**
  - Microcontroller: Arduino Uno / Nano compatible board.
  - Acoustic Sensor: KY-037 sound sensor module (analog comparator + electret microphone).
  - Particulate Sensor: Optical dust sensor (referred to in docs as p.25 / GP2Y1010AU0F or similar optical scatter sensor).
  - Interface: Serial USB connection (`COM3`, 9600 baud, carriage-return delimited).
  - Sensing Paradigm: Unidirectional open-loop push or polled periodic read.
  - No on-board actuators, no active calibration, no pan-tilt mechanism, no local filtering.

- **Host Laptop:**
  - Target: Qualcomm Snapdragon X Elite platform with Hexagon NPU.
  - Current Actual Execution: Standard Python process running on CPU/OS; optional Qualcomm GenieX QNN library wrapper in `ai/npu_engine.py` for Gemma-4 GGUF weights, with cloud Cirrascale fallback.

- **Client Mobile Device:**
  - Android device running CameraX and basic GPS provider, with optional static TFLite task vision classifier.

---

## 5. Current Software

- **Programming Languages:** Python 3.10+ (Backend, AI, Cloud, MCP), Kotlin (Android Mobile), JavaScript/HTML (Web Dashboard).
- **Frameworks:** FastAPI, Uvicorn, SQLAlchemy, Pydantic, OpenCV (cv2), Pillow (PIL), PySerial, Requests/HTTPX.
- **Storage:** Local SQLite databases (`backend.db` and `cloud_data.db`).
- **Dependencies:** Specified in `requirements.txt`.

---

## 6. Current Decision Logic

The core decision logic resides entirely in `backend/fusion/scoring.py` and is evaluated as follows:

$$\text{Score}_{\text{base}} = \begin{cases} \text{progress}, & \text{if visual stage is valid and } \text{progress} > 0 \\ 0.0, & \text{otherwise} \end{cases}$$

1. **RERA Adjustment:**
   - If nearest project status contains `"approved"`: $\text{Score} \leftarrow \text{Score} + 15.0$
   - If nearest project status contains `"disputed"` or `"unauthorized"`: $\text{Score} \leftarrow \text{Score} - 30.0$; $\text{Risk} \leftarrow \text{"High"}$
   - If no project within 500m: $\text{Score} \leftarrow \text{Score} - 10.0$

2. **IoT Sensor Adjustment (Only if `sensor_status == "connected"`):**
   - High activity confirmation: If $\text{noise} > 70.0\,\text{dB}$ and $\text{PM2.5} > 40.0\,\mu\text{g/m}^3$: $\text{Score} \leftarrow \text{Score} + 10.0$
   - Activity mismatch: If $\text{progress} \in (10.0, 90.0)$ and $\text{noise} < 50.0\,\text{dB}$: $\text{Score} \leftarrow \text{Score} - 15.0$
   - Environmental hazard trigger: If $\text{noise} > 85.0\,\text{dB}$ or $\text{PM2.5} > 100.0\,\mu\text{g/m}^3$ or $\text{PM10} > 150.0\,\mu\text{g/m}^3$: append warning text.

3. **Clipping:**
   $$\text{Development Score} = \min(100.0, \max(0.0, \text{Score}))$$

---

## 7. Current Limitations

1. **Pure Feedforward Open-Loop Execution:** The system takes inputs, produces an output score, and terminates. It exerts no action on the environment, adjusts no sensing parameters, commands no movement, and executes no re-observation cycle.
2. **Naive Hardcoded Spatial Correlation:** Distance between phone and IoT node is checked with a static threshold of $50\,\text{m}$. It assumes isotropic, point-source alignment with zero consideration of acoustic attenuation ($1/r^2$), wind advection, wall occlusions, or multi-path reflections.
3. **Static Temporal Threshold:** Hardcoded 30-second window fails to account for intermittent construction activity (e.g., concrete mixer idle periods, excavator duty cycles, shift breaks).
4. **Uncalibrated Sensor Drift and Fouling:** The optical particulate sensor is directly exposed to construction dust without purge cycles, zero-point calibration, or fouling compensation.
5. **Arbitrary Heuristic Weighting:** The $+15, -30, +10, -15$ score adjustments are arbitrary numbers without statistical or physical justification.
6. **No Uncertainty Quantification:** Predictions are treated as deterministic scalar points without state covariances or Bayesian confidence intervals.

---

## 8. Current Assumptions

1. **Spatial Collocation Assumption:** Assumes that if a mobile phone is within 50m of an Arduino node, they are observing the exact same physical event.
2. **Instantaneous Emission Assumption:** Assumes that active construction must continuously emit $>70\,\text{dB}$ noise and $>40\,\mu\text{g/m}^3$ dust simultaneously at the sensor's exact position.
3. **Sensor Reliability Assumption:** Assumes raw KY-037 analog readings and optical dust scatter accurately reflect true ambient environmental state without environmental cross-sensitivity (e.g., ambient road traffic, humidity spikes, wind noise).
4. **Visual Ground-Truth Assumption:** Assumes single-frame 2D photos provided by crowdsourced users can reliably determine total 3D structural development progress.
