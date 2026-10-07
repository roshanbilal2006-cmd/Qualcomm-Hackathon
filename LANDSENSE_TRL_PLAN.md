# LandSense AI: Technology Readiness Level (TRL) Plan

**Document Version:** 1.0.0  
**Inspection Date:** 2026-10-07  
**Target Invention:** Dual-Rate Information-Theoretic Directed Observation Engine (DIT-DOE)

---

## 1. TRL Definitions & Current Truth Assessment

| TRL Level | Standard Definition | Current LandSense Status | Assessment & Gap Analysis |
| :---: | :--- | :---: | :--- |
| **TRL 1** | Basic principles observed and reported | **DONE** | Physical laws of acoustic attenuation ($1/r^2$) and atmospheric particulate advection-diffusion established. |
| **TRL 2** | Technology concept and/or application formulated | **DONE** | Conceptual coupling of continuous IoT boundary sensing with directed mobile visual inspection formulated. |
| **TRL 3** | Analytical and experimental critical function and/or characteristic proof-of-concept | **IN PROGRESS** | Algorithmic state estimation, Fisher Information view planning, and closed-loop recalibration implemented in `/landsense_invention/`. Simulation benchmarks executed. |
| **TRL 4** | Component and/or breadboard validation in laboratory environment | **NOT DONE** | Hardware Arduino node streaming live data to laptop with physical acoustic speaker/dust generator in a controlled bench environment. |
| **TRL 5** | Component and/or breadboard validation in relevant environment | **NOT DONE** | Deployment at an active urban construction perimeter with live wind, traffic noise, and real mobile field walk. |
| **TRL 6** | System/subsystem model or prototype demonstration in a relevant environment | **NOT DONE** | Multi-day autonomous perimeter deployment across multiple registered municipal sites. |
| **TRL 7** | System prototype demonstration in an operational environment | **NOT DONE** | Full integration with municipal environmental enforcement agency and contractor compliance dashboards. |

### Honest Current TRL: **TRL 3**
The original repository was at TRL 2 (a collection of separate mock scripts and basic UI demos). With the implementation and simulation validation of the DIT-DOE engine, the project attains **TRL 3**. It is NOT at TRL 4 or 5 because physical bench coupling and field trials have not yet occurred.

---

## 2. TRL 3 Evidence Checklist

- [x] **DONE**: Mathematical formulation of 2D atmospheric advection-diffusion and acoustic barrier attenuation model.
- [x] **DONE**: Recursive Extended Kalman Filter (EKF) tracking latent source position $(x_s, y_s)$, emission strength $Q$, barrier attenuation $A_{\text{barrier}}$, and structural stage.
- [x] **DONE**: Fisher Information Matrix (FIM) optimization engine calculating optimal camera pose $(x^*, y^*, \theta^*)$.
- [x] **DONE**: Closed-loop recalibration mechanism updating stationary IoT transfer function from visual feedback.
- [x] **DONE**: Multi-baseline comparative simulation (Baseline 0, Baseline 1, Baseline 2, Baseline 3 vs Proposed).
- [x] **DONE**: Automated Kill-Test experiment runner with formal pass/kill criterion.

---

## 3. TRL 4 Requirements (Controlled Bench / Laboratory Environment)

To advance from TRL 3 to TRL 4, the following physical laboratory steps must be completed:

1. **Hardware Ingestion Validation:**
   - Physical Arduino Uno connected via USB serial (`COM3`, 9600 baud) running teammates' firmware.
   - Sensor inputs: Physical KY-037 electret microphone + optical particulate sensor (GP2Y1010 / PM2.5 sensor).
   - Status: **NOT DONE** (Teammates currently building/debugging firmware; software adapter ready in `mcp/adapters/sensor/arduino_sensor_adapter.py`).

2. **Controlled Acoustic & Particulate Excitation:**
   - Acoustic test: Calibrated audio loudspeaker playing 1 kHz tone burst and recorded construction excavator audio at varying SPL ($60\text{--}85\,\text{dBA}$).
   - Particulate test: Incense stick or aerosol test chamber generating controlled particulate plume.
   - Status: **NOT DONE**.

3. **Snapdragon NPU Local Inference Integration:**
   - Execute quantized Gemma-4 or MobileNet on Qualcomm Hexagon NPU via GenieX/LiteRT to extract visual features in $<100\,\text{ms}$ on laptop.
   - Status: **NOT DONE** (GenieX environment is machine-dependent; fallback OpenCV pipeline functional).

4. **Closed-Loop Software Handshake:**
   - Host laptop reads real serial stream $\to$ updates EKF $\to$ generates inspection waypoint on mobile UI $\to$ mobile camera returns frame $\to$ EKF collapses covariance.
   - Status: **NOT DONE** (Fully implemented in simulation; ready for hardware binding).

---

## 4. TRL 5 Requirements (Relevant Agricultural / Construction Field Environment)

To advance from TRL 4 to TRL 5, the system must undergo outdoor field validation:

1. **Perimeter Deployment:**
   - Install the Arduino IoT node on a temporary tripod/pole at an active construction site perimeter (or university building construction site).
   - Node powered by 5V USB battery bank.

2. **Environmental Noise & Wind Handling:**
   - Connect live weather API or local anemometer to supply real-time wind vector $\mathbf{u} = (u_x, u_y)$.
   - Verify EKF stability under ambient traffic noise ($>70\,\text{dBA}$) without divergence.

3. **Mobile Field Walk:**
   - Operator walking along public sidewalk with Android app.
   - Verify GPS accuracy ($\pm 3\text{--}5\,\text{m}$) and compass heading stability.
   - Receive directed waypoint notification $\to$ walk to coordinate $\to$ snap photo $\to$ observe real-time score and covariance convergence.

---

## 5. Milestone Road-Map Summary

```
[Current Status: TRL 3] ──► [Lab Bench Integration: TRL 4] ──► [Outdoor Field Trial: TRL 5]
 • EKF & FIM Math            • Arduino serial link              • Real construction site
 • Closed-Loop Simulation    • Acoustic/dust bench test         • GPS walk on sidewalk
 • Kill-Test Verified        • Snapdragon NPU local loop        • True ambient noise & wind
 (COMPLETED TODAY)           (ESTIMATED: 1-2 DAYS)              (ESTIMATED: 3-5 DAYS)
```
