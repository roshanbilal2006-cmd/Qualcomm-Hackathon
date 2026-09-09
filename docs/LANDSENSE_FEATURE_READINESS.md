# Feature Readiness Matrix

| Feature | Current Status | Real Data? | Production Ready? | Phase to Fix |
| --- | --- | --- | --- | --- |
| image capture | Partially implemented by mobile app and API contract | Mixed | No | Phase 1-2 |
| GPS | API contract and payload route present | Partial real | No | Phase 1-2 |
| timestamp | Route and API contract present | Partial real | No | Phase 1-2 |
| image preprocessing | Implemented in AI engine | Partial real | No | Phase 1-2 |
| cloud AI | Implemented as cloud route and LLM service | Partial real | No | Phase 1-2 |
| structured AI output | Implemented in AI engine and backend | Partial real | No | Phase 1-2 |
| Ollama | Not implemented | No | No | Phase 2 |
| sensor ingestion | Implemented in MCP sensor path | Mock/demo | No | Phase 2 |
| noise | Implemented via dummy sensor adapter | Mock/demo | No | Phase 2 |
| PM2.5 | Implemented via dummy sensor adapter | Mock/demo | No | Phase 2 |
| PM10 | Implemented via dummy sensor adapter | Mock/demo | No | Phase 2 |
| RERA/project data | Implemented via mock RERA provider | Mock | No | Phase 2 |
| spatial correlation | Partially implemented conceptually | Partial real | No | Phase 2 |
| temporal correlation | Partially implemented conceptually | Partial real | No | Phase 2 |
| scoring | Rule-based implementation exists | Real rules | Partial | Phase 2 |
| risk | Not cleanly separated from scoring | Partial | No | Phase 2 |
| confidence | AI output and scoring include confidence-like features | Partial | No | Phase 2 |
| evidence consistency | Not fully implemented | No | No | Phase 2 |
| offline mode | Partially documented; no verified end-to-end offline mode | Partial | No | Phase 2 |
| synchronization | Local/cloud route and HTTP model described | Partial | No | Phase 2 |
| chat | Cloud chat route exists; uses LLMService | Partial real | No | Phase 2 |
| map | Heatmap route exists in cloud | Partial real | No | Phase 2 |
| history | Observation history and retrieval exist | Partial real | No | Phase 2 |
| security | Basic CORS and route patterns; secret scanning needed | Partial | No | Phase 2 |
