# Patent Specification & Formal Claim Tree

**Title:** DUAL-RATE CYBER-PHYSICAL SYSTEM AND METHOD FOR CLOSED-LOOP STRUCTURAL AND ENVIRONMENTAL MONITORING VIA INFORMATION-THEORETIC DIRECTED VIEW PLANNING

---

## Technical Field

The present disclosure relates generally to the technical fields of cyber-physical systems, recursive state estimation, environmental sensing, and active computer vision. More particularly, the disclosure relates to a closed-loop system and method for estimating non-stationary emission rates, structural development milestones, and physical perimeter shielding parameters at a construction or land development site by coupling continuous stationary telemetry with episodic mobile visual sensing steered by Fisher Information view planning.

---

## Background of the Invention

Perimeter environmental monitoring around urban construction sites is critical for public health, regulatory compliance, and worker safety. Conventional monitoring architectures generally fall into two disconnected categories:
1. **Stationary Environmental Loggers:** Fixed sensor stations positioned along site boundaries continuously record sound pressure levels (dBA) and airborne particulate concentrations ($\text{PM}_{2.5}$, $\text{PM}_{10}$). However, stationary boundary sensors suffer from a fundamental **Spatial Observability Deficit**: a scalar reading is a complex convolution of source emission intensity, source distance, wind advection vectors, and non-line-of-sight physical barrier attenuation (e.g., perimeter hoardings, boundary walls, and earth berms). A single stationary sensor cannot mathematically decouple these variables, leading to frequent false alarms or undetected violations.
2. **Episodic Visual Surveying:** Drones or handheld mobile devices capture high-resolution images to assess structural progress. However, visual capture requires significant human labor, battery consumption, and compute bandwidth on edge neural processors. Operating visual cameras continuously is computationally and logistically prohibitive.

Prior art systems fail to provide a closed-loop mechanism linking continuous physical telemetry with episodic visual sensing. Consequently, existing systems either waste extensive resources capturing redundant, unguided photographs from occluded vantage points or rely on uncalibrated, drifting stationary sensors that misrepresent true site emissions. There exists an acute technical need for a closed-loop cyber-physical system that dynamically steers mobile visual observers based on physical information gain to resolve environmental boundary parameters and recalibrate stationary sensor models.

---

## Summary of the Invention

The present disclosure addresses the deficiencies of the prior art by providing a **Dual-Rate Information-Theoretic Directed Observation Engine (DIT-DOE)**.

In one embodiment, a computer-implemented method comprises:
1. Receiving a continuous stream of environmental telemetry (acoustic sound pressure level and particulate concentration) from at least one stationary sensor node positioned at a perimeter boundary.
2. Recursively updating a state estimate vector $\hat{\mathbf{x}}_t$ and state error covariance matrix $\mathbf{P}_t$ in a state estimator using non-linear forward physical models of acoustic spherical divergence and 2D atmospheric advection-diffusion, wherein the state vector includes source spatial coordinates $(x_s, y_s)$, source emission rate $Q_{\text{emit}}$, perimeter barrier attenuation $A_{\text{barrier}}$, and structural progress percentage $S_{\text{progress}}$.
3. Evaluating an information deficit criterion over a spatial/structural subspace of the covariance matrix.
4. Upon satisfying the information deficit criterion, evaluating a Fisher Information Matrix (FIM) over a plurality of candidate boundary inspection poses $p = (x_c, y_c, \theta_c)$ and identifying an optimal inspection pose $p^*$ that maximizes a D-optimality objective function penalizing observer transit cost.
5. Transmitting a directed inspection instruction to an episodic mobile device commanding physical acquisition of an optical image at the optimal inspection pose $p^*$.
6. Ingesting targeted visual features extracted from the optical image, updating the state estimator to resolve the physical barrier attenuation parameter $A_{\text{barrier}}$ and source coordinates, thereby collapsing the covariance matrix; and
7. Recalibrating the forward physical model of the stationary sensor node using the resolved barrier attenuation parameter, enabling accurate subsequent continuous source emission inversion without requiring additional optical images.

---

## Brief Description of the Drawings

- **FIG. 1** illustrates the cyber-physical system architecture, showing the interaction between the physical construction site, the stationary IoT node, the edge computing device, and the directed mobile observer.
- **FIG. 2** is a schematic diagram of the closed-loop perception and recalibration cycle.
- **FIG. 3** depicts the geometric line-of-sight view-planning model evaluated along site boundary sidewalks.
- **FIG. 4** is a flowchart of the recursive dual-rate Extended Kalman Filter and Fisher Information dispatch routine.
- **FIG. 5** is a comparative graph illustrating emission rate estimation error across baselines and the proposed method.
- **FIG. 6** illustrates the empirical covariance collapse upon receiving targeted visual feedback.

---

## Detailed Description of the Preferred Embodiments

### 1. Mathematical State-Space Formulation
The latent state vector $\mathbf{x} \in \mathbb{R}^5$ is modeled in discrete time $k$ as:
$$\mathbf{x}_k = \begin{bmatrix} x_{s,k} \\ y_{s,k} \\ Q_{\text{emit},k} \\ A_{\text{barrier},k} \\ S_{\text{progress},k} \end{bmatrix}$$

The continuous-time state transition equation is:
$$\mathbf{x}_{k+1} = \mathbf{x}_k + \mathbf{f}(\mathbf{x}_k)\Delta t + \mathbf{w}_k$$
where $\mathbf{w}_k \sim \mathcal{N}(\mathbf{0}, \mathbf{Q}_{\text{proc}})$, with process noise covariance:
$$\mathbf{Q}_{\text{proc}} = \operatorname{diag}(\sigma_{pos}^2, \sigma_{pos}^2, \sigma_Q^2, \sigma_{barrier}^2, \sigma_{prog}^2)$$

### 2. Forward Physical Observation Models
The stationary IoT telemetry vector $\mathbf{z}_{\text{iot}} = [L_{p,\text{meas}}, C_{\text{PM2.5},\text{meas}}]^T$ is modeled via non-linear observation equations:
$$L_p = L_w(Q) - 20\log_{10}\left(\sqrt{(x_{\text{node}} - x_s)^2 + (y_{\text{node}} - y_s)^2}\right) - 11 - A_{\text{barrier}} - A_{\text{air}}$$
$$C_{\text{PM2.5}} = C_{\text{ambient}} + \frac{0.35 \cdot Q_{\text{emit}}}{2\pi \|\mathbf{u}\| \sigma_y(x) \sigma_z(x)} \exp\left(-\frac{y_{\text{crosswind}}^2}{2\sigma_y(x)^2}\right) \cdot (1 - \eta_{\text{barrier}}(A_{\text{barrier}}))$$
where:
$$\eta_{\text{barrier}}(A_{\text{barrier}}) = \min(0.8, 0.04 \cdot A_{\text{barrier}})$$

### 3. Fisher Information View Planning
For each candidate pose $p = (x_c, y_c, \theta_c) \in \mathcal{P}$:
1. Compute geometric distance $d = \|\mathbf{x}_c - \hat{\mathbf{x}}_s\|$ and line-of-sight bearing $\phi = \operatorname{atan2}(\hat{y}_s - y_c, \hat{x}_s - x_c)$.
2. Evaluate geometric Field-of-View attenuation factor:
   $$\text{FOV}(p) = \max\left(0.05, \cos\left(\min\left(\frac{\pi}{2}, |\theta_c - \phi|\right)\right)\right) \cdot \min\left(1.0, \frac{r_{\text{site}}}{d}\right)$$
3. Compute the observation Jacobian $\mathbf{H}_{\text{vis}}(p)$ and dynamic observation covariance $\mathbf{R}_{\text{vis}}(p)$.
4. Construct the Fisher Information Matrix:
   $$\mathbf{F}(p) = \mathbf{H}_{\text{vis}}(p)^T \mathbf{R}_{\text{vis}}(p)^{-1} \mathbf{H}_{\text{vis}}(p)$$
5. Solve the constrained D-optimality objective:
   $$p^* = \arg\max_{p \in \mathcal{P}} \left[ \log \det\left(\mathbf{P}_k^{-1} + \mathbf{F}(p)\right) - \lambda_{\text{travel}} \cdot \|\mathbf{x}_{\text{user}} - \mathbf{x}_p\| \right]$$

---

## Patent Claims Tree

### Claim 1 (Independent Method Claim)
A computer-implemented method for closed-loop cyber-physical monitoring of a land development site, comprising:
1. receiving, by at least one processor, a continuous stream of environmental telemetry from at least one stationary sensor node positioned along a perimeter boundary of the site, wherein the environmental telemetry comprises acoustic sound pressure measurements and particulate matter concentration measurements;
2. recursively updating, by the at least one processor, a state vector $\hat{\mathbf{x}}_t$ and an error covariance matrix $\mathbf{P}_t$ in a state estimator using a non-linear forward physical model parameterizing source spatial coordinates, a source emission flux, and a physical perimeter barrier attenuation parameter;
3. evaluating an information deficit criterion over a subspace of the error covariance matrix;
4. upon satisfaction of the information deficit criterion, evaluating a Fisher Information Matrix over a plurality of candidate boundary observation poses and selecting an optimal observation pose that maximizes a multi-objective information-gain function penalizing physical observer transit distance;
5. transmitting an inspection instruction to an episodic mobile device commanding acquisition of an optical image at the optimal observation pose;
6. receiving targeted visual features extracted from the optical image acquired at the optimal observation pose and executing a visual measurement update in the state estimator to resolve the physical perimeter barrier attenuation parameter and collapse the error covariance matrix; and
7. recalibrating the non-linear forward physical model of the stationary sensor node using the resolved physical perimeter barrier attenuation parameter, wherein subsequent continuous telemetry from the stationary sensor node is inverted to estimate the source emission flux without requiring additional optical images.

### Claim 2 (Dependent Claim - Barrier Model)
The method of claim 1, wherein the non-linear forward physical model calculates acoustic attenuation according to spherical wave spreading combined with an insertion loss term corresponding to the physical perimeter barrier attenuation parameter, and calculates particulate matter concentration according to a two-dimensional atmospheric advection-diffusion equation modulated by a barrier filtration efficiency function parameterized by the physical perimeter barrier attenuation parameter.

### Claim 3 (Dependent Claim - D-Optimality)
The method of claim 1, wherein the multi-objective information-gain function computes a D-optimality metric defined by the log-determinant of the sum of an inverse prior covariance matrix and the Fisher Information Matrix for each candidate boundary observation pose.

### Claim 4 (Dependent Claim - Dynamic FOV Weighting)
The method of claim 3, wherein evaluating the Fisher Information Matrix comprises dynamically scaling an observation noise covariance matrix inversely proportional to a geometric Field-of-View alignment factor between a camera optical axis of the candidate pose and a line-of-sight vector to an estimated emission epicenter.

### Claim 5 (Dependent Claim - Subspace Trigger)
The method of claim 1, wherein the information deficit criterion is evaluated by summing variances of the source spatial coordinates and the physical perimeter barrier attenuation parameter in the error covariance matrix, independent of emission flux variance.

### Claim 6 (Dependent Claim - Innovation Anomaly)
The method of claim 1, further comprising evaluating an innovation residual vector between received stationary telemetry and predicted telemetry, and triggering selection of the optimal observation pose when a norm of the innovation residual vector exceeds an anomaly threshold.

### Claim 7 (Dependent Claim - Cooldown Governor)
The method of claim 1, further comprising enforcing a temporal cooldown interval between successive transmissions of inspection instructions, wherein inspection instructions are suppressed once the error covariance matrix collapses below a stability threshold.

### Claim 8 (Dependent Claim - Cross-Bearing Triangulation)
The method of claim 1, wherein the targeted visual features extracted from the optical image comprise triangulated Cartesian coordinates of an active machinery epicenter and a visual barrier classification index.

### Claim 9 (Dependent Claim - Dual-Rate Sampling)
The method of claim 1, wherein the continuous stream of environmental telemetry is ingested at a sample rate between $0.5\,\text{Hz}$ and $10\,\text{Hz}$, and wherein episodic optical images are acquired at an average frequency at least fifty times lower than the continuous telemetry sample rate.

### Claim 10 (Dependent Claim - Atmospheric Wind Coupling)
The method of claim 2, further comprising ingesting real-time wind speed and wind direction vectors from a micro-meteorological feed, wherein the advection-diffusion equation rotates spatial coordinate axes parallel to the ingested wind direction vector.

---

### Claim 11 (Independent System Claim)
A closed-loop cyber-physical monitoring system for a land development site, comprising:
1. at least one stationary sensor node disposed at a perimeter boundary of the site, comprising an acoustic transducer and an optical particulate transducer configured to transmit continuous environmental telemetry;
2. an episodic mobile observation client comprising an optical camera, a location receiver, an orientation sensor, and a wireless network interface;
3. an edge computing system communicatively coupled to the at least one stationary sensor node and the episodic mobile observation client, comprising one or more processors and a memory storing instructions that, when executed, cause the one or more processors to:
   - maintain a recursive state estimator tracking a continuous latent state vector comprising emission source coordinates, an emission rate, and a physical perimeter barrier attenuation parameter;
   - update the recursive state estimator using incoming continuous environmental telemetry and a physical dispersion model;
   - evaluate an information deficit metric over the recursive state estimator;
   - upon detecting an information deficit, compute a Fisher Information Matrix across candidate boundary coordinates and dispatch a navigation waypoint commanding the episodic mobile observation client to capture an image at an optimal viewpoint;
   - update the physical perimeter barrier attenuation parameter in the recursive state estimator based on visual features extracted from the captured image; and
   - recalibrate the physical dispersion model in closed loop to invert subsequent telemetry from the stationary sensor node.

### Claim 12 (Dependent Claim - Edge NPU Acceleration)
The system of claim 11, wherein the edge computing system comprises a Neural Processing Unit (NPU), and wherein the visual features are extracted on the NPU using a quantized neural network.

### Claim 13 (Dependent Claim - Serial Microcontroller Interface)
The system of claim 11, wherein the at least one stationary sensor node comprises an Arduino-compatible microcontroller communicating with the edge computing system via a Universal Asynchronous Receiver-Transmitter (UART) serial interface.

### Claim 14 (Dependent Claim - Acoustic Bandpass Filter)
The system of claim 11, wherein the acoustic transducer comprises an electret microphone coupled to an analog comparator configured to isolate low-frequency impulsive mechanical sound pressure signatures between $10\,\text{Hz}$ and $50\,\text{Hz}$.

### Claim 15 (Dependent Claim - Directional Arrow Guidance)
The system of claim 11, wherein the episodic mobile observation client renders a graphical compass rose and a directional guidance vector pointing towards the optimal observation pose.

---

### Claim 16 (Independent Non-Transitory Medium Claim)
A non-transitory computer-readable storage medium storing instructions that, when executed by one or more processors, cause the one or more processors to execute the method of claim 1.
