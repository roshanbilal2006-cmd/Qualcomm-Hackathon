# Current vs Future Matrix

| Capability | Current implementation | Future target |
| --- | --- | --- |
| Cloud AI | Cirrascale/AISuite provider in `ai/engine.py` | OpenRouter primary cloud AI |
| Local AI | Optional NPU local path and OpenCV fallback | Ollama local/offline fallback |
| Sensor | Demo mode by default with `DummySensorAdapter`; live mode has `ArduinoSensorAdapter` path | Real hardware sensor provider |
| RERA | `MockRERAAdapter` default from `mock_rera.json` | Real verified RERA or regulated data provider |
| Evidence schema | Current backend response structure is partial and route-specific | Common structured evidence schema |
| Spatial validation | Haversine distance + threshold 50m in code | Robust validation and coverage |
| Temporal validation | Timestamp delta threshold 30s in code | Robust temporal evidence handling |
| Reliability | Not a distinct engine | Reliability and trust engine |
| Contradiction detection | Not explicit | Explicit conflict engine |
| Evidence fusion | Rule-based in scoring | Confidence-aware fusion |
| Development score | Rule-based progression and RERA/sensor adjustments | Evidence-based scoring |
| Observation trust | Not implemented as a specific engine | Observation trust score |
| Offline | Local NPU path plus OpenCV fallback; not a verified end-to-end offline system | Full local/offline AI inference |
