# LANDSense Data Origin Model

This document defines the current Phase 1 data-origin semantics.

## Categories

### REAL
Data obtained from a corresponding physical or verified external source.

### SIMULATED
Data produced by explicit simulation, including `DummySensorAdapter` and the demo sensor path.

### MOCK
Static data records such as `MockRERAAdapter` that are intentionally local, in-repo, testable, and non-verified.

### CROWDSOURCED/EXTERNAL
Environmental or project data that is not measured directly by the physical sensor but is imported from nearby project records or external context.

### UNKNOWN
Origin cannot be confirmed from the current request or service context.

## Repository mapping

- `DummySensorAdapter` → `SIMULATED`
- `MockRERAAdapter` → `MOCK`
- `LiveRERAAdapter` → `UNKNOWN` until a verifiable live URL and API contract are configured
- Crowdsourced project environmental readings → `CROWDSOURCED/EXTERNAL`
- Main backend observations with no verified sensor route → `UNKNOWN`

## Semantic constraints

The following are forbidden without explicit labeling:

- `SIMULATED -> REAL`
- `MOCK -> VERIFIED`
- `MISSING -> CURRENT TIME`
- `MISSING GPS -> HARD_CODED GPS`
- `INVALID -> VALID`
- `UNAVAILABLE -> CONNECTED`
- `CROWDSOURCED -> PHYSICAL SENSOR`
- `TEST FIXTURE -> PRODUCTION EVIDENCE`
