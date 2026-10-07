# LandSense AI: Decisive Kill-Test Plan

**Document Version:** 1.0.0  
**Target Invention:** Dual-Rate Information-Theoretic Directed Observation Engine (DIT-DOE)  
**Location:** `/landsense_invention/experiments/KILL_TEST_PLAN.md`

---

## 1. The Core Scientific Hypothesis

> **Hypothesis:** Under non-line-of-sight perimeter boundary shielding ($A_{\text{barrier}} > 0$) and intermittent construction emission bursts, the proposed DIT-DOE closed-loop mechanism achieves $>35\%$ lower emission estimation RMSE, reduces mobile visual capture burden by $\ge 40\%$ compared to periodic baselines, and converges on true physical barrier attenuation within $\pm 2.5\,\text{dB}$ by actively steering mobile camera observations to coordinates that maximize the Fisher Information Matrix determinant.

---

## 2. Experimental Environment & Setup

- **Simulation Engine:** `landsense_invention/simulation/site_simulator.py`
- **Duration:** 120 time steps per run (representing 2 hours of continuous site activity at 1-minute sampling intervals).
- **Statistical Power:** 5 independent Monte Carlo seeds ($42, 101, 202, 303, 404$).
- **Physical Ground Truth:**
  - True source location: $(12.0\,\text{m}, -10.0\,\text{m})$.
  - True perimeter barrier attenuation: $A_{\text{barrier}} = 12.5\,\text{dB}$ (corrugated metal sheet/concrete boundary wall).
  - True initial progress: $38.0\%$.
  - Duty cycles: Periodic state switching between `IDLE` ($Q = 80\,\mu\text{g/s}, L_w = 70\,\text{dBA}$), `EXCAVATING` ($Q = 650\,\mu\text{g/s}, L_w = 96\,\text{dBA}$), and `ROCK_BREAKING` ($Q = 1200\,\mu\text{g/s}, L_w = 104\,\text{dBA}$).
  - Boundary IoT node position: $(0.0\,\text{m}, 55.0\,\text{m})$ (North perimeter).
  - Atmospheric wind: $2.8\,\text{m/s}$ blowing at $45^\circ$ (North-East).

---

## 3. The 4 Baselines vs Proposed Method

### Baseline 0: Current LandSense System
- **Mechanism:** Unguided crowdsourced photo uploads at random walk intervals ($\sim 3\%$ probability per step). Raw PM2.5 converted linearly to emission rate. No state estimation, no spatial dispersion model, no barrier attenuation modeling.
- **Role:** Demonstrates performance of the existing, unmodified repository.

### Baseline 1: Naive Threshold Heuristic
- **Mechanism:** Triggers photo alert whenever raw noise exceeds $74\,\text{dBA}$ or PM2.5 exceeds $50\,\mu\text{g/m}^3$. User captures from a random nearby spot along perimeter without view-planning.
- **Role:** Standard IoT alerting heuristic used in commercial pollution monitors.

### Baseline 2: Periodic Scheduled Inspection + EKF
- **Mechanism:** Fixed timer captures photos every $T = 25$ steps regardless of uncertainty. Ingested into EKF, but captured from the user's natural walking pose without view-planning.
- **Role:** Standard robotics/Kalman filtering approach without active perception.

### Baseline 3: Greedy Closest Capture + EKF
- **Mechanism:** EKF active trigger fires, but the user immediately snaps a photo from the closest point on the sidewalk looking directly inwards, ignoring Fisher Information or line-of-sight angle.
- **Role:** Standard greedy spatial search baseline.

### Proposed Method: DIT-DOE
- **Mechanism:** EKF state estimator + spatial/barrier covariance trigger ($P_{\text{spatial}} > 30.0$) + Fisher Information view-planner optimizing candidate poses + closed-loop barrier recalibration.

---

## 4. Evaluation Metrics

1. **Emission Estimation RMSE ($Q_{\text{RMSE}}$):** Root Mean Squared Error of estimated source emission flux $\hat{Q}_t$ vs true $Q_t^*$ ($\mu\text{g/s}$).
2. **Emission Estimation MAE ($Q_{\text{MAE}}$):** Mean Absolute Error ($\mu\text{g/s}$).
3. **Progress Estimation RMSE ($S_{\text{RMSE}}$):** Error in structural progress completion percentage ($\%$).
4. **Capture Budget:** Total number of mobile photos demanded from human users across the trajectory.
5. **Barrier Recalibration Error ($\Delta A_{\text{barrier}}$):** Absolute difference $|\hat{A}_{\text{barrier}} - 12.5\,\text{dB}|$.

---

## 5. Formal Kill Conditions

The proposed invention core will be **KILLED** if any of the following occur:
1. **Kill Condition 1 (No Meaningful Advantage Over Current System):**
   $Q_{\text{RMSE}}(\text{Proposed}) \ge 0.65 \times Q_{\text{RMSE}}(\text{Baseline 0})$ ($<35\%$ improvement).
2. **Kill Condition 2 (Inefficient Resource Usage):**
   Proposed method demands more mobile captures than Baseline 2 while failing to achieve lower RMSE.
3. **Kill Condition 3 (Fisher Information Provides Zero Gain):**
   Proposed method achieves identical or worse error compared to Baseline 3 (Greedy closest).
4. **Kill Condition 4 (Failure to Converge on Physical Parameter):**
   $|\hat{A}_{\text{barrier}} - 12.5\,\text{dB}| > 2.5\,\text{dB}$.

---

## 6. Execution Command

To execute the automated kill-test battery and generate verification logs:

```bash
python -m landsense_invention.experiments.kill_test_runner
python -m landsense_invention.experiments.generate_report
```
