# LandSense AI: Technical Limitations & Boundary Conditions

**Document Version:** 1.0.0  
**Inspection Date:** 2026-10-07  
**Location:** `/landsense_invention/reports/LIMITATIONS.md`

---

## 1. Physical & Environmental Limitations

1. **Severe Micro-Meteorological Turbulence & Calm Air Inversion:**
   - The 2D Gaussian plume advection model assumes a non-zero mean wind vector ($\|\mathbf{u}\| \ge 0.5\,\text{m/s}$).
   - Under dead-calm atmospheric conditions ($\|\mathbf{u}\| < 0.2\,\text{m/s}$), advection collapses and molecular/turbulent diffusion dominates isotropic accumulation. The plume equations exhibit numerical sensitivity as $\|\mathbf{u}\| \to 0$, requiring transition to a spherical puff diffusion model.
2. **Extreme Non-Line-of-Sight Urban Canyons:**
   - In dense metropolitan cores surrounded by $30$-story skyscrapers, acoustic reflections (multi-path echoes) and building wake turbulence create complex recirculation eddies that deviate from simple ISO 9613-2 propagation.
   - The current EKF treats multi-path reflections as measurement noise; high multi-path environments increase localization uncertainty.
3. **Multiple Spatially Distributed Simultaneous Emitters:**
   - The current model tracks a single predominant construction epicenter $(x_s, y_s)$ per parcel (e.g., the primary excavator or piling rig).
   - If a large 10-acre site operates three separate heavy machines simultaneously in opposite corners, the single-source model estimates an effective geometric centroid of emissions rather than resolving distinct multi-point sources. A multi-target Gaussian Mixture / Particle Filter would be required to resolve multi-source clusters.

---

## 2. Sensor & Transducer Limitations

1. **Acoustic Background Saturation in Heavy Traffic:**
   - If the site boundary borders a major highway where ambient traffic noise exceeds $80\,\text{dBA}$, the signal-to-noise ratio (SNR) for acoustic construction detection degrades significantly unless spectral filtering (e.g., bandpass isolating hydraulic hammer frequencies at 10–30 Hz) is applied.
2. **Optical Particulate Hygroscopic Growth:**
   - Low-cost optical dust sensors (such as the GP2Y1010 or low-cost laser scatter sensors) are sensitive to relative humidity. At relative humidity $>80\%$, water vapor condenses on airborne particles, inflating apparent optical scatter and causing PM2.5 overestimation unless heated inlet tubes or hygroscopic growth correction curves are applied.

---

## 3. Human & Operational Constraints

1. **Restricted Physical Sidewalk Access:**
   - The Fisher Information view-planner assumes candidate waypoints along public sidewalks are accessible to pedestrians.
   - If a candidate waypoint falls on private property, a water body, or an active traffic lane, the trajectory solver must incorporate cadastral right-of-way exclusion masks.
2. **Operator Compliance Delay:**
   - The system computes an optimal inspection waypoint and dispatches an instruction to a human mobile user.
   - If the user takes 5 to 10 minutes to walk to the designated location, transient high-frequency emission bursts may have subsided by the time the camera frame is captured. The EKF handles this by decaying the temporal relevance of the innovation residual.

---

## 4. Computational & Platform Bounds

1. **Snapdragon NPU Quantization Precision:**
   - Visual feature extraction on the Qualcomm Hexagon NPU relies on 4-bit or 8-bit quantized weights (Gemma-4 / MobileNet). Low-light or extreme dust conditions can reduce classification confidence, requiring explicit uncertainty bounds in the observation noise covariance matrix $\mathbf{R}_{\text{vis}}$.
2. **Serial Latency & Buffer Overflow:**
   - When Arduino Uno streams at 9600 baud, UART transmission latency is $\sim 10\text{--}15\,\text{ms}$. If baud rate is misconfigured or serial polling stalls, stale readings can briefly enter the EKF buffer.
