"""
LandSense Invention: Closed-Loop Perception & Inspection Governor - Calibrated
Module: landsense_invention.controller.closed_loop_governor

Coordinates continuous IoT estimation, spatial/structural information triggers,
Fisher view-planning, and closed-loop parameter recalibration upon visual feedback.
"""

from typing import Dict, Any, Optional, Tuple
import numpy as np

from landsense_invention.sensing.telemetry_model import PhysicalDispersionModel
from landsense_invention.controller.state_estimator import DualRateStateEstimator
from landsense_invention.controller.information_engine import FisherInformationEngine


class ClosedLoopGovernor:
    """
    Main controller orchestrating the cyber-physical perception loop.
    Trigger is specifically governed by spatial and barrier uncertainty
    P_spatial = P[0,0] + P[1,1] + P[3,3], which camera view-planning resolves.
    """

    def __init__(
        self,
        sensor_x: float = 0.0,
        sensor_y: float = 55.0,  # boundary node at North perimeter
        site_radius_m: float = 50.0,
        spatial_uncertainty_threshold: float = 30.0,  # spatial+barrier variance threshold
        residual_trigger_threshold: float = 22.0,      # major anomaly trigger
        cooldown_steps: int = 20,                      # min steps between photo requests
    ):
        self.sensor_x = sensor_x
        self.sensor_y = sensor_y
        self.site_radius = site_radius_m
        self.spatial_uncertainty_threshold = spatial_uncertainty_threshold
        self.residual_threshold = residual_trigger_threshold
        self.cooldown_steps = cooldown_steps

        self.disp = PhysicalDispersionModel()
        self.estimator = DualRateStateEstimator(
            initial_source_guess=(0.0, 0.0),
            site_radius_m=site_radius_m,
            dispersion_model=self.disp,
        )
        self.info_engine = FisherInformationEngine(site_radius_m=site_radius_m)

        self.step_counter = 0
        self.last_trigger_step = -cooldown_steps
        self.total_dispatches = 0
        self.total_visual_updates = 0

    def process_continuous_telemetry(
        self,
        noise_db: float,
        pm25: float,
        current_user_x: float,
        current_user_y: float,
        dt: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Processes continuous incoming IoT telemetry step:
        1. Predict & EKF Update
        2. Evaluate Information Deficit over spatial/structural subspace
        3. If triggered, compute optimal Fisher waypoint
        """
        self.step_counter += 1

        self.estimator.predict(dt=dt)
        iot_result = self.estimator.update_iot(
            noise_meas_db=noise_db,
            pm25_meas=pm25,
            sensor_x=self.sensor_x,
            sensor_y=self.sensor_y,
        )

        # Spatial and barrier variance: P[0,0] + P[1,1] + P[3,3]
        spatial_var = float(self.estimator.P[0, 0] + self.estimator.P[1, 1] + self.estimator.P[3, 3])
        res_norm = iot_result["residual_norm"]

        can_trigger = (self.step_counter - self.last_trigger_step) >= self.cooldown_steps
        high_spatial_uncertainty = spatial_var > self.spatial_uncertainty_threshold
        high_residual = res_norm > self.residual_threshold

        action_required = can_trigger and (high_spatial_uncertainty or high_residual)
        dispatch_instruction = None

        if action_required:
            self.last_trigger_step = self.step_counter
            self.total_dispatches += 1

            est_summary = self.estimator.get_state_summary()
            waypoint = self.info_engine.select_optimal_waypoint(
                current_user_x=current_user_x,
                current_user_y=current_user_y,
                estimated_source_x=est_summary["source_x"],
                estimated_source_y=est_summary["source_y"],
                prior_covariance=self.estimator.P,
            )

            dispatch_instruction = {
                "action": "DISPATCH_DIRECTED_INSPECTION",
                "reason": "HIGH_SPATIAL_UNCERTAINTY" if high_spatial_uncertainty else "EMISSION_INNOVATION_ANOMALY",
                "target_x": waypoint["optimal_x"],
                "target_y": waypoint["optimal_y"],
                "target_azimuth_deg": waypoint["optimal_azimuth_deg"],
                "expected_info_score": waypoint["best_score"],
                "spatial_variance": round(spatial_var, 2),
            }

        return {
            "step": self.step_counter,
            "iot_result": iot_result,
            "spatial_variance": spatial_var,
            "state_estimate": self.estimator.get_state_summary(),
            "action_dispatch": dispatch_instruction,
            "trigger_fired": action_required,
        }

    def process_episodic_visual(
        self,
        visual_progress_pct: float,
        visual_barrier_attenuation_db: float,
        camera_x: float,
        camera_y: float,
        camera_azimuth_deg: float,
        visual_source_x: Optional[float] = None,
        visual_source_y: Optional[float] = None,
        visibility_quality: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Processes targeted visual feedback uploaded by client:
        Collapses covariance, updates barrier parameters, recalibrates future IoT model.
        """
        self.total_visual_updates += 1
        vis_result = self.estimator.update_visual(
            visual_progress_pct=visual_progress_pct,
            visual_barrier_attenuation_db=visual_barrier_attenuation_db,
            visual_source_x=visual_source_x,
            visual_source_y=visual_source_y,
            visibility_quality=visibility_quality,
        )

        state_after = self.estimator.get_state_summary()

        return {
            "visual_result": vis_result,
            "state_after_recalibration": state_after,
            "covariance_reduction_pct": round(
                100.0 * (1.0 - (vis_result["covariance_trace_after_visual"] / max(1.0, vis_result.get("covariance_trace_before", 200.0)))),
                1
            ),
        }
