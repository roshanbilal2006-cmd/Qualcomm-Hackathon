# Feature Readiness Matrix

| Feature | Current Status | Real Data? | Production Ready? | Phase to Fix |
| --- | --- | --- | --- | --- |
| camera | PARTIAL | Mixed | No | Phase 2 |
| image preprocessing | PARTIAL | Partial real | No | Phase 2 |
| AI | PARTIAL | Cirrascale/AISuite cloud/image contract | No | Phase 2 |
| GPS | PARTIAL | Request-based, with fallback coordinate behavior | No | Phase 2 |
| timestamp | PARTIAL | Request and sensor timestamps | No | Phase 2 |
| sensors | MOCK | Dummy sensor adapter default | No | Phase 2 |
| noise | MOCK | Dummy data generator | No | Phase 2 |
| PM2.5 | MOCK | Dummy data generator | No | Phase 2 |
| PM10 | MOCK | Dummy data generator | No | Phase 2 |
| RERA | MOCK | MockRERAAdapter by default | No | Phase 2 |
| spatial correlation | PARTIAL | Haversine by code, 50m path | No | Phase 2 |
| temporal correlation | PARTIAL | 30-second timestamp threshold path | No | Phase 2 |
| scoring | WORKING | Rule-based scoring | Partial | Phase 2 |
| risk | WORKING | Derived from scoring rules | Partial | Phase 2 |
| confidence | PARTIAL | AI engine output and scoring confidence | Partial | Phase 2 |
| evidence consistency | NOT IMPLEMENTED | None | No | Phase 2 |
| evidence fusion | PARTIAL | Rule-based sensor and RERA fusion | Partial | Phase 2 |
| observation trust | NOT IMPLEMENTED | None | No | Phase 2 |
| offline | PARTIAL | Local NPU path exists; no full local AI verified | No | Phase 2 |
| synchronization | PARTIAL | Cloud/local observation sync path | No | Phase 2 |
| chat | PARTIAL | Cloud LLM service route | Partial | Phase 2 |
| map | PARTIAL | Heatmap endpoint exists | Partial | Phase 2 |
| history | PARTIAL | Local/cloud observation history | Partial | Phase 2 |
| security | PARTIAL | Basic config exists; secrets need secure config | No | Phase 2 |
