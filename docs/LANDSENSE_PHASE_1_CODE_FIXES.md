# LANDSense Phase 1 Code Fixes

This log records the source-code corrections that are intentionally limited to the Phase 1 integrity and safety baseline.

## Code corrections

| Bug/Issue | File | Previous behavior | New behavior | Test |
| --- | --- | --- | --- | --- |
| Dummy sensor data masquerading as physical hardware | `mcp/adapters/sensor/dummy_sensor_adapter.py` | `get_status()` returned `connected` and the read payload contained no explicit simulated origin metadata | The adapter now emits `sensor_source="dummy"` and `data_origin="simulated"`, and `get_status()` returns `simulated` | `backend/tests/test_phase1_corrections.py` |
| Invalid timestamp fabricating now-time | `backend/fusion/correlation.py` | `parse_iso_timestamp()` caught parse failures and returned `datetime.now(timezone.utc)` | `parse_iso_timestamp()` returns `None` for malformed or missing timestamps and no synthetic current timestamp is introduced | `backend/tests/test_phase1_corrections.py` |
| Missing/invalid sensor GPS silently using untrusted coordinates | `backend/pipeline/orchestrator.py` and `backend/fusion/correlation.py` | `sensor_lat = sensor_data.get("latitude", 12.9716)` and `sensor_lon = sensor_data.get("longitude", 77.7500)` replaced missing coordinates with hardcoded fallback values | The pipeline reads coordinates only if present; missing coordinates remain missing and correlation returns `False` for unavailable spatial evidence | `backend/tests/test_phase1_corrections.py` |
| Crowdsourced/external environmental values masquerading as physical sensor evidence | `backend/pipeline/orchestrator.py` | Crowdsourced RERA project fields could overwrite the `sensor_status` into `connected (crowdsourced)` | Crowdsourced/external values remain explicitly labeled as `crowdsourced` and are no longer claimed to be physical hardware measurements | Covered by the pipeline semantics and test scaffold |
| Mock RERA source origin not preserved | `mcp/adapters/rera/mock_rera_adapter.py` | `MockRERAAdapter` returned records without a source label | `MockRERAAdapter` tags loaded records with `source='mock'` and `data_origin='mock'` | `backend/tests/test_phase1_corrections.py` |
| Live RERA stub silently presenting an unconfigured state as live | `mcp/adapters/rera/live_rera_adapter.py` | `get_status()` could report `live` even when base URL was missing | `get_status()` now reports `unavailable` and error messages explicitly forbid silent fallback to mock data | `backend/tests/test_phase1_corrections.py` |
| OpenRouter/OpenCV mislabel in AI health shape | `ai/main.py` | `/health` exposed `ai_backend` as `openrouter_opencv` and openrouter fields | `/health` now reports `cirrascale_opencv` and suppresses openrouter field leakage to keep current provider truthful | semantic consistency update |

## Intentionally Deferred

- OpenRouter integration
- Ollama integration
- real sensor replacement
- live RERA integration
- evidence consistency engine
- evidence fusion engine
- observation trust score
- new scoring algorithm
- major database redesign
- major UI redesign
