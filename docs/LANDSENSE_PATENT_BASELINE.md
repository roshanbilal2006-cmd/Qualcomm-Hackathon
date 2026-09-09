# LANDSense Patent-Relevant Technical Baseline

This document is a technical baseline only. It does not claim that the project is novel, patentable, or completed.

## Existing Technical Features

Current / Already implemented:

- Multi-source observation shape: image, site GPS, timestamp, sensor values, project data, and backend route object.
- Image analysis by OpenCV and/or AI service contract in `ai/engine.py`.
- Backend scoring and structured response object from `calculate_development_score()`.
- Sensor and RERA adapter interfaces in `mcp/` with mock/demo defaults.
- Basic Haversine distance and timestamp validation in `backend/fusion/correlation.py`.
- Cloud/local AI or NPU service separation in `ai/main.py` and `ai/npu_engine.py`.

## Partial Technical Features

Current / Partially implemented:

- Sensor correlation between phone and sensor: implemented via threshold and distance gates, but depends on dummy and hardcoded fallback values.
- Spatial validation: implemented by Haversine distance and 50m threshold, but can be bypassed by fallback coordinates and missing GPS.
- Temporal validation: implemented by time difference 30 seconds in code, but only as a rough rule.
- Confidence: included as an AI response and final response field but not a full reliability engine.
- Evidence fusion: represented by scoring and scoring reasons from multiple sources but not a robust common evidence consistency engine.

## Missing Future Mechanisms

Not implemented / missing:

- Observation trust and reliability engine
- Contradiction detection or evidence consistency engine
- Confidence-aware evidence fusion architecture
- Full real RERA, sensor, and server-backed source reliability validation
- Verified local/offline Ollama fallback
- Verified end-to-end cloud/local AI continuity

## Important Research Note

The repository has a set of technical mechanisms that may deserve later patent-relevant investigation, but the current code is not the future evidence consistency and fusion engine described in the long-range product direction.
