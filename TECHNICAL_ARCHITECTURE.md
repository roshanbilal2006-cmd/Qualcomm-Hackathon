# LandSense AI: Technical Architecture Specification

**Document Version:** 1.0.0  
**Target Invention:** Dual-Rate Information-Theoretic Directed Observation Engine (DIT-DOE)  
**Location:** `/landsense_invention/architecture/TECHNICAL_ARCHITECTURE.md`

---

## 1. System Architecture Overview

The DIT-DOE architecture operates as a dual-rate cyber-physical observer that bridges stationary high-rate/low-spatial-resolution IoT telemetry with episodic low-rate/high-spatial-resolution mobile visual sensing.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        PHYSICAL ENVIRONMENT                            │
│  - Evolving construction structure: x_s, y_s                           │
│  - Non-stationary emission source: Q_dust(t), Q_acoustic(t)            │
│  - Physical perimeter boundary barrier: A_barrier                      │
└───────────────────▲────────────────────────────────┬───────────────────┘
                    │                                │
        Targeted Camera Capture                      │ 1 Hz Continuous
        at Optimal Waypoint (x*, y*, θ*)             │ Telemetry (dBA, PM)
                    │                                │
                    │                                ▼
┌───────────────────┴──────────┐   ┌─────────────────────────────────────┐
│    EPISODIC MOBILE OBSERVER   │   │     CONTINUOUS IoT BOUNDARY NODE    │
│  - Android CameraX           │   │  - Arduino Uno / Nano               │
│  - Snapdragon Hexagon NPU    │   │  - KY-037 Electret Microphone       │
│  - GPS + Compass Azimuth     │   │  - Optical Dust Sensor (GP2Y1010)   │
└───────────────▲──────────────┘   └──────────────────┬──────────────────┘
                │                                     │
       Directed Inspection                            │ Raw Continuous
       Instruction u_t                                │ Stream z_t
                │                                     │
                │                                     ▼
┌───────────────┴────────────────────────────────────────────────────────┐
│                     DIT-DOE REAL-TIME CONTROLLER                       │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ 1. State Estimator (Extended Kalman Filter)                    │   │
│   │    State: x = [x_s, y_s, Q_emit, A_barrier, Progress]^T        │   │
│   │    Covariance: P_t                                             │   │
│   │    Forward Physical Models: Acoustic Spreading & Advection     │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ 2. Information Deficit Trigger                                 │   │
│   │    Evaluates spatial/barrier covariance:                       │   │
│   │    P_spatial = P[0,0] + P[1,1] + P[3,3] > Threshold            │   │
│   │    OR Innovation Residual |r_t| > Anomaly_Threshold            │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ 3. Fisher Information View-Planning Engine                     │   │
│   │    Evaluates candidate boundary poses p = (x_c, y_c, θ_c)      │   │
│   │    Maximizes D-optimality log det(P^-1 + FIM(p)) - Cost        │   │
│   │    Dispatches optimal waypoint p* = (x*, y*, θ*)               │   │
│   └───────────────────────────────┬────────────────────────────────┘   │
│                                   │                                    │
│                                   ▼                                    │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ 4. Closed-Loop Model Recalibration                             │   │
│   │    Visual feedback resolves A_barrier and source coordinates;  │   │
│   │    Collapses P_spatial;                                        │   │
│   │    Recalibrates stationary IoT inversion model parameters.     │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. State-Space Formulation

The continuous-time latent state vector is defined as:
$$\mathbf{x}(t) = \begin{bmatrix} x_s(t) \\ y_s(t) \\ Q_{\text{emit}}(t) \\ A_{\text{barrier}}(t) \\ S_{\text{progress}}(t) \end{bmatrix} \in \mathbb{R}^5$$

- $x_s(t), y_s(t)$: Epicenter coordinates of active mechanical excavation/breaking (meters).
- $Q_{\text{emit}}(t)$: Airborne particulate mass emission rate ($\mu\text{g/s}$).
- $A_{\text{barrier}}(t)$: Effective acoustic insertion loss of perimeter shielding barrier (dBA).
- $S_{\text{progress}}(t)$: Integrated structural development progress percentage ($0\text{--}100\%$).

### Process Dynamics Model:
$$\mathbf{x}_{k+1} = \mathbf{x}_k + \begin{bmatrix} 0 \\ 0 \\ 0 \\ 0 \\ \alpha \cdot \max(0, Q_{\text{emit}} - Q_{\text{idle}}) \end{bmatrix} \Delta t + \mathbf{w}_k$$
where $\mathbf{w}_k \sim \mathcal{N}(\mathbf{0}, \mathbf{Q}_{\text{proc}})$, with process covariance:
$$\mathbf{Q}_{\text{proc}} = \operatorname{diag}\left(\sigma_{pos}^2, \sigma_{pos}^2, \sigma_Q^2, \sigma_{barrier}^2, \sigma_{prog}^2\right)$$

---

## 3. Observation Models

### 1. High-Rate Stationary IoT Telemetry $\mathbf{z}_{\text{iot}} = [L_p, C_{\text{PM2.5}}]^T$
$$\begin{aligned}
h_1(\mathbf{x}) &= L_w(Q) - 20\log_{10}\left(\sqrt{(x_{\text{sensor}} - x_s)^2 + (y_{\text{sensor}} - y_s)^2}\right) - 11 - A_{\text{barrier}} \\
h_2(\mathbf{x}) &= C_{\text{ambient}} + \frac{0.35 \cdot Q_{\text{emit}}}{2\pi \|\mathbf{u}\| \sigma_y \sigma_z} \exp\left(-\frac{y_{\text{crosswind}}^2}{2\sigma_y^2}\right) \cdot (1 - \eta_{\text{barrier}}(A_{\text{barrier}}))
\end{aligned}$$
where:
$$\eta_{\text{barrier}}(A_{\text{barrier}}) = \min(0.8, 0.04 \cdot A_{\text{barrier}})$$

### 2. Episodic Mobile Visual Observation $\mathbf{z}_{\text{vis}} = [A_{\text{obs}}, S_{\text{obs}}, x_{\text{obs}}, y_{\text{obs}}]^T$
$$\mathbf{z}_{\text{vis}} = \mathbf{H}_{\text{vis}} \mathbf{x} + \mathbf{v}_{\text{vis}}(p)$$
where $\mathbf{v}_{\text{vis}}(p) \sim \mathcal{N}(\mathbf{0}, \mathbf{R}_{\text{vis}}(p))$, and the observation noise covariance dynamically scales with viewing geometry:
$$\mathbf{R}_{\text{vis}}(p) = \operatorname{diag}\left(\frac{\sigma_A^2}{\text{FOV}(p)^2}, \frac{\sigma_S^2}{\text{FOV}(p)^2}, \frac{\sigma_{pos}^2}{\text{FOV}(p)^2}, \frac{\sigma_{pos}^2}{\text{FOV}(p)^2}\right)$$

---

## 4. Fisher Information View-Planning Algorithm

For every candidate inspection pose $p = (x_c, y_c, \theta_c)$ along accessible perimeter sidewalks:
1. Compute Line-of-Sight Azimuth and Distance:
   $$d = \sqrt{(x_c - \hat{x}_s)^2 + (y_c - \hat{y}_s)^2}, \quad \phi = \operatorname{atan2}(\hat{y}_s - y_c, \hat{x}_s - x_c)$$
2. Compute Field-of-View Factor:
   $$\text{FOV}(p) = \max\left(0.05, \cos\left(\min\left(\frac{\pi}{2}, |\theta_c - \phi|\right)\right)\right) \cdot \min\left(1.0, \frac{r_{\text{site}}}{d}\right)$$
3. Compute Pose Observation Jacobian $\mathbf{H}(p)$ and Fisher Information Matrix:
   $$\mathbf{F}(p) = \mathbf{H}(p)^T \mathbf{R}_{\text{vis}}(p)^{-1} \mathbf{H}(p)$$
4. Compute D-Optimality Objective with Travel Cost:
   $$\mathcal{J}(p) = \log \det\left(\mathbf{P}_t^{-1} + \mathbf{F}(p)\right) - \lambda_{\text{travel}} \cdot \|\mathbf{x}_{\text{user}} - \mathbf{x}_p\|$$
5. Dispatch Optimal Pose:
   $$p^* = \arg\max_{p \in \mathcal{P}} \mathcal{J}(p)$$

---

## 5. Software Component Mapping

| Subsystem | Source Module | Function |
| :--- | :--- | :--- |
| **Physical Telemetry Model** | `landsense_invention/sensing/telemetry_model.py` | Implements acoustic spherical spreading and Gaussian plume dispersion equations. |
| **Recursive State Estimator** | `landsense_invention/controller/state_estimator.py` | Executes EKF prediction, continuous IoT update, and episodic visual update. |
| **Fisher View-Planner** | `landsense_invention/controller/information_engine.py` | Dispatches optimal inspection poses maximizing FIM log-determinant. |
| **Closed-Loop Governor** | `landsense_invention/controller/closed_loop_governor.py` | Orchestrates triggers, dispatches, and parameter recalibration. |
| **Ground-Truth Simulator** | `landsense_invention/simulation/site_simulator.py` | Simulates construction duty cycles, noise, and geometric camera captures. |
| **Comparative Baselines** | `landsense_invention/experiments/baselines.py` | Implements Baselines 0, 1, 2, 3 and Proposed DIT-DOE. |
| **Kill-Test Battery** | `landsense_invention/experiments/kill_test_runner.py` | Automated multi-seed benchmark runner with hypothesis evaluation. |
