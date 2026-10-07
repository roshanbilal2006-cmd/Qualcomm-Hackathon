"""
LandSense Invention: Recursive Dual-Rate State Estimator (EKF) - Refined
Module: landsense_invention.controller.state_estimator

Implements an Extended Kalman Filter tracking:
x = [x_source, y_source, Q_emission, A_barrier, progress_pct]^T
with analytical/properly-scaled Jacobian perturbations and adaptive observation noise.
"""

import math
import numpy as np
from typing import Dict, Any, Tuple, Optional
from landsense_invention.sensing.telemetry_model import PhysicalDispersionModel


class DualRateStateEstimator:
    """
    Tracks latent construction epicenter, emission flux, perimeter barrier
    attenuation, and stage progress using continuous IoT telemetry and
    episodic visual observations.
    """

    STATE_DIM = 5  # [x_s, y_s, Q_emit, A_barrier, progress]

    def __init__(
        self,
        initial_source_guess: Tuple[float, float] = (0.0, 0.0),
        site_radius_m: float = 50.0,
        dispersion_model: Optional[PhysicalDispersionModel] = None,
    ):
        self.disp = dispersion_model or PhysicalDispersionModel()
        self.site_radius = site_radius_m

        # State vector: [x_s, y_s, Q_emit (ug/s), A_barrier (dB), progress (%)]
        self.x = np.array([
            initial_source_guess[0],
            initial_source_guess[1],
            400.0,    # initial guess of emission rate
            5.0,      # initial guess of barrier attenuation
            35.0,     # initial guess of progress
        ], dtype=float)

        # State Error Covariance Matrix P
        self.P = np.diag([
            (site_radius_m * 0.4) ** 2,  # spatial uncertainty ~20m
            (site_radius_m * 0.4) ** 2,
            (250.0) ** 2,                # emission uncertainty
            (8.0) ** 2,                  # barrier attenuation uncertainty
            (10.0) ** 2,                 # progress percentage uncertainty
        ])

        # Process Noise Covariance Q (per second)
        self.Q_proc = np.diag([
            0.02,    # machinery position drift
            0.02,
            8.0,     # emission rate process variation
            0.0005,  # barrier physical changes
            0.005,   # progress increment
        ])

        # Continuous Measurement Noise Covariance
        self.R_iot = np.diag([
            2.0 ** 2,    # acoustic noise sensor noise (dBA)
            5.0 ** 2,    # PM2.5 sensor noise (ug/m3)
        ])

    def predict(self, dt: float = 1.0) -> None:
        """
        State transition prediction step: x_{t|t-1} = F x_{t-1}
        """
        # Slight drift in progress over time during active emissions
        if self.x[2] > 100.0:
            self.x[4] = min(100.0, self.x[4] + 0.004 * dt)

        # Propagate covariance
        self.P = self.P + self.Q_proc * dt

        # Enforce physical constraints
        self.x[2] = max(0.0, self.x[2])             # Q_emit >= 0
        self.x[3] = max(0.0, min(25.0, self.x[3]))    # A_barrier in [0, 25] dB
        self.x[4] = max(0.0, min(100.0, self.x[4]))

    def update_iot(
        self,
        noise_meas_db: float,
        pm25_meas: float,
        sensor_x: float,
        sensor_y: float,
        nominal_lw: float = 95.0,
    ) -> Dict[str, Any]:
        """
        Non-linear EKF measurement update from continuous IoT telemetry.
        Measurement vector: z = [noise_db, pm25]^T
        """
        z = np.array([noise_meas_db, pm25_meas])

        # Predicted measurement h(x)
        h_noise = self.disp.compute_acoustic_spl(
            source_x=self.x[0],
            source_y=self.x[1],
            source_sound_power_lw=nominal_lw,
            sensor_x=sensor_x,
            sensor_y=sensor_y,
            barrier_attenuation_db=self.x[3],
        )

        barrier_filt = min(0.8, self.x[3] * 0.04)
        h_pm25, _ = self.disp.compute_particulate_concentration(
            source_x=self.x[0],
            source_y=self.x[1],
            emission_rate_q=self.x[2],
            sensor_x=sensor_x,
            sensor_y=sensor_y,
            barrier_filtration_efficiency=barrier_filt,
        )
        h_pred = np.array([h_noise, h_pm25])
        residual = z - h_pred

        # Scaled finite differences for robust numerical Jacobians
        eps_vec = np.array([0.1, 0.1, 5.0, 0.1, 0.5])
        H = np.zeros((2, self.STATE_DIM))

        for j in range(self.STATE_DIM):
            x_pert = self.x.copy()
            x_pert[j] += eps_vec[j]

            h_n_pert = self.disp.compute_acoustic_spl(
                source_x=x_pert[0],
                source_y=x_pert[1],
                source_sound_power_lw=nominal_lw,
                sensor_x=sensor_x,
                sensor_y=sensor_y,
                barrier_attenuation_db=x_pert[3],
            )
            b_filt_pert = min(0.8, x_pert[3] * 0.04)
            h_p_pert, _ = self.disp.compute_particulate_concentration(
                source_x=x_pert[0],
                source_y=x_pert[1],
                emission_rate_q=x_pert[2],
                sensor_x=sensor_x,
                sensor_y=sensor_y,
                barrier_filtration_efficiency=b_filt_pert,
            )
            H[0, j] = (h_n_pert - h_noise) / eps_vec[j]
            H[1, j] = (h_p_pert - h_pm25) / eps_vec[j]

        # S = H P H^T + R
        S = H @ self.P @ H.T + self.R_iot
        K = self.P @ H.T @ np.linalg.inv(S)

        self.x = self.x + K @ residual

        # Joseph form update
        I = np.eye(self.STATE_DIM)
        I_KH = I - K @ H
        self.P = I_KH @ self.P @ I_KH.T + K @ self.R_iot @ K.T

        # Constraints
        self.x[2] = max(0.0, self.x[2])
        self.x[3] = max(0.0, min(25.0, self.x[3]))
        self.x[4] = max(0.0, min(100.0, self.x[4]))

        return {
            "residual_norm": float(np.linalg.norm(residual)),
            "covariance_trace": float(np.trace(self.P)),
            "predicted_spl": h_noise,
            "predicted_pm25": h_pm25,
        }

    def update_visual(
        self,
        visual_progress_pct: float,
        visual_barrier_attenuation_db: float,
        visual_source_x: Optional[float] = None,
        visual_source_y: Optional[float] = None,
        visibility_quality: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Episodic measurement update from directed mobile visual capture.
        Observation noise R_visual scales inversely with visibility quality.
        """
        trace_before = float(np.trace(self.P))
        quality = max(0.15, min(1.0, visibility_quality))

        # Dynamic noise covariance conditioned on view geometry
        sigma_barrier = max(0.4, 1.2 / quality)
        sigma_progress = max(0.8, 2.5 / quality)
        sigma_pos = max(1.0, 3.5 / quality)

        if visual_source_x is not None and visual_source_y is not None:
            z_v = np.array([
                visual_barrier_attenuation_db,
                visual_progress_pct,
                visual_source_x,
                visual_source_y,
            ])
            H_v = np.zeros((4, self.STATE_DIM))
            H_v[0, 3] = 1.0  # barrier
            H_v[1, 4] = 1.0  # progress
            H_v[2, 0] = 1.0  # source_x
            H_v[3, 1] = 1.0  # source_y
            R_v = np.diag([
                sigma_barrier ** 2,
                sigma_progress ** 2,
                sigma_pos ** 2,
                sigma_pos ** 2,
            ])
        else:
            z_v = np.array([
                visual_barrier_attenuation_db,
                visual_progress_pct,
            ])
            H_v = np.zeros((2, self.STATE_DIM))
            H_v[0, 3] = 1.0
            H_v[1, 4] = 1.0
            R_v = np.diag([
                sigma_barrier ** 2,
                sigma_progress ** 2,
            ])

        h_v = H_v @ self.x
        residual_v = z_v - h_v

        S_v = H_v @ self.P @ H_v.T + R_v
        K_v = self.P @ H_v.T @ np.linalg.inv(S_v)

        self.x = self.x + K_v @ residual_v

        I = np.eye(self.STATE_DIM)
        I_KH = I - K_v @ H_v
        self.P = I_KH @ self.P @ I_KH.T + K_v @ R_v @ K_v.T

        self.x[2] = max(0.0, self.x[2])
        self.x[3] = max(0.0, min(25.0, self.x[3]))
        self.x[4] = max(0.0, min(100.0, self.x[4]))

        return {
            "covariance_trace_before": trace_before,
            "covariance_trace_after_visual": float(np.trace(self.P)),
            "updated_barrier_db": float(self.x[3]),
            "updated_progress_pct": float(self.x[4]),
            "updated_source_x": float(self.x[0]),
            "updated_source_y": float(self.x[1]),
        }

    def get_state_summary(self) -> Dict[str, Any]:
        std = np.sqrt(np.diag(self.P))
        return {
            "source_x": round(float(self.x[0]), 2),
            "source_x_std": round(float(std[0]), 2),
            "source_y": round(float(self.x[1]), 2),
            "source_y_std": round(float(std[1]), 2),
            "emission_rate_q": round(float(self.x[2]), 1),
            "emission_q_std": round(float(std[2]), 1),
            "barrier_attenuation_db": round(float(self.x[3]), 2),
            "barrier_std": round(float(std[3]), 2),
            "progress_pct": round(float(self.x[4]), 1),
            "progress_std": round(float(std[4]), 1),
            "covariance_trace": round(float(np.trace(self.P)), 2),
        }
