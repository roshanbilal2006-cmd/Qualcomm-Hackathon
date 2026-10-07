# LandSense AI: Invention Discovery & Adversarial Audit Archive

This directory contains the complete technical discovery trail, reverse-engineering analyses, and adversarial audits conducted during the formal patentability hardening of **LandSense AI**.

---

## Document Index

1. **[INVENTION_DISCOVERY_REPORT.md](INVENTION_DISCOVERY_REPORT.md)**
   - Complete executive summary of the invention discovery process, from hackathon heuristic deconstruction to the formulation of DIT-DOE and governing physical equations.

2. **[CANDIDATE_INVENTIONS_ANALYSIS.md](CANDIDATE_INVENTIONS_ANALYSIS.md)**
   - Comprehensive matrix evaluating 5 candidate inventive mechanisms across technical feasibility, EPO Art. 56 inventive step, USPTO §101 subject-matter eligibility, and hardware compatibility.

3. **[INVENTION_ADVERSARIAL_ATTACK.md](INVENTION_ADVERSARIAL_ATTACK.md)**
   - Red-team adversarial patent examination mimicking harsh EPO / USPTO examiner rejections, prior art citations (D1-D4), and required remediations.

4. **[LANDSENSE_CURRENT_ARCHITECTURE.md](LANDSENSE_CURRENT_ARCHITECTURE.md)**
   - Reverse-engineering of the original codebase (`backend/fusion/scoring.py`, `backend/pipeline/orchestrator.py`, `mcp/adapters/sensor/arduino_sensor_adapter.py`) detailing all inputs, outputs, and limitations.

5. **[NON_INVENTIVE_FEATURES.md](NON_INVENTIVE_FEATURES.md)**
   - Deconstruction of standard/ordinary features in the repository that do NOT constitute an inventive step (VLM inference, UART polling, GPS distance filtering, additive scoring).

---

## Active Invention Documents (Root Level)

For active legal filings, teammate implementation instructions, and formal claims:
- **[TEAM_HANDOVER.md](../../TEAM_HANDOVER.md)** — Master integration guide with role-by-role contracts.
- **[PATENT_SPECIFICATION_AND_CLAIMS.md](../../PATENT_SPECIFICATION_AND_CLAIMS.md)** — Complete 15-claim patent specification (Revision 2.0).
- **[INVENTIVE_STEP_DEFENSE.md](../../INVENTIVE_STEP_DEFENSE.md)** — Full EPO/USPTO legal defense and 30-seed statistical benchmark tables.
- **[landsense_invention/](../../landsense_invention/)** — Executable Python reference implementation and benchmark scripts.
