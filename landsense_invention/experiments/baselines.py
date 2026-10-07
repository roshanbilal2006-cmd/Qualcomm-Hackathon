"""
LandSense Invention: Experimental Baselines Implementation - Refined
Module: landsense_invention.experiments.baselines

Implements Baseline 0 (Current LandSense), Baseline 1 (Threshold Heuristic),
Baseline 2 (Periodic Scheduled), Baseline 3 (Greedy Closest), and Proposed (DIT-DOE).
"""

import math
import random
import numpy as np
from typing import Dict, Any, List, Tuple

from landsense_invention.simulation.site_simulator import ConstructionSiteSimulator
from landsense_invention.controller.closed_loop_governor import ClosedLoopGovernor
from landsense_invention.controller.state_estimator import DualRateStateEstimator


class BaselineRunner:
    """
    Executes comparative benchmarks across all baselines on identical
    simulation trajectories.
    """

    def __init__(self, steps: int = 120, seed: int = 101):
        self.steps = steps
        self.seed = seed

    def run_baseline_0_current_landsense(self) -> Dict[str, Any]:
        """
        Baseline 0: Current LandSense architecture.
        Takes unguided crowdsourced photos at random intervals.
        Computes score using naive additive rule.
        Zero state estimation, zero barrier compensation.
        """
        sim = ConstructionSiteSimulator(seed=self.seed)
        random.seed(self.seed)

        q_errors = []
        progress_errors = []
        capture_count = 0

        for t in range(self.steps):
            telemetry, gt = sim.step()

            # Random user photo upload (~ every 30 steps)
            if random.random() < 0.033:
                capture_count += 1
                cam_angle = random.uniform(0, 2.0 * math.pi)
                cam_x = 55.0 * math.cos(cam_angle)
                cam_y = 55.0 * math.sin(cam_angle)
                cam_azimuth = random.uniform(0, 360)
                cam_obs = sim.simulate_camera_capture(cam_x, cam_y, cam_azimuth)
                raw_progress = cam_obs["visual_progress_pct"]
            else:
                raw_progress = 35.0  # static fallback

            # Current system calculates naive emission without barrier compensation
            naive_q = max(0.0, (telemetry.dust_pm25 - 25.0) * 14.0)

            q_errors.append(abs(naive_q - gt["true_q"]))
            progress_errors.append(abs(raw_progress - gt["true_progress"]))

        return {
            "name": "Baseline 0: Current LandSense (Unguided / Rule-Based)",
            "q_rmse": float(np.sqrt(np.mean(np.array(q_errors) ** 2))),
            "q_mae": float(np.mean(q_errors)),
            "progress_rmse": float(np.sqrt(np.mean(np.array(progress_errors) ** 2))),
            "captures_required": capture_count,
            "barrier_estimated": None,
        }

    def run_baseline_1_threshold_heuristic(self) -> Dict[str, Any]:
        """
        Baseline 1: Common heuristic.
        Triggers inspection whenever raw noise > 74 dBA or PM2.5 > 50 ug/m3.
        User walks to nearest random spot along perimeter.
        """
        sim = ConstructionSiteSimulator(seed=self.seed)
        random.seed(self.seed)

        q_errors = []
        progress_errors = []
        capture_count = 0
        current_progress = 35.0
        cooldown = 0

        for t in range(self.steps):
            telemetry, gt = sim.step()
            cooldown = max(0, cooldown - 1)

            if cooldown == 0 and (telemetry.noise_db > 74.0 or telemetry.dust_pm25 > 50.0):
                capture_count += 1
                cooldown = 25
                cam_angle = random.uniform(0, 2.0 * math.pi)
                cam_x = 55.0 * math.cos(cam_angle)
                cam_y = 55.0 * math.sin(cam_angle)
                cam_obs = sim.simulate_camera_capture(cam_x, cam_y, math.degrees(math.atan2(-cam_y, -cam_x)))
                current_progress = cam_obs["visual_progress_pct"]

            est_q = max(0.0, (telemetry.dust_pm25 - 25.0) * 14.0)
            q_errors.append(abs(est_q - gt["true_q"]))
            progress_errors.append(abs(current_progress - gt["true_progress"]))

        return {
            "name": "Baseline 1: Threshold Heuristic Trigger",
            "q_rmse": float(np.sqrt(np.mean(np.array(q_errors) ** 2))),
            "q_mae": float(np.mean(q_errors)),
            "progress_rmse": float(np.sqrt(np.mean(np.array(progress_errors) ** 2))),
            "captures_required": capture_count,
            "barrier_estimated": None,
        }

    def run_baseline_2_periodic_scheduled(self) -> Dict[str, Any]:
        """
        Baseline 2: Periodic scheduled capture every 25 timesteps with EKF,
        but without active information-gain view planning (user captures at current walk pose).
        """
        sim = ConstructionSiteSimulator(seed=self.seed)
        estimator = DualRateStateEstimator(dispersion_model=sim.disp)

        q_errors = []
        progress_errors = []
        capture_count = 0
        user_angle = 0.0

        for t in range(self.steps):
            telemetry, gt = sim.step()

            # User walks naturally along perimeter
            user_angle += 0.05
            user_x = 55.0 * math.cos(user_angle)
            user_y = 55.0 * math.sin(user_angle)

            estimator.predict(dt=1.0)
            estimator.update_iot(
                noise_meas_db=telemetry.noise_db,
                pm25_meas=telemetry.dust_pm25,
                sensor_x=sim.sensor_x,
                sensor_y=sim.sensor_y,
            )

            # Fixed schedule: capture every 25 steps
            if (t + 1) % 25 == 0:
                capture_count += 1
                cam_obs = sim.simulate_camera_capture(
                    user_x, user_y, math.degrees(math.atan2(-user_y, -user_x))
                )
                estimator.update_visual(
                    visual_progress_pct=cam_obs["visual_progress_pct"],
                    visual_barrier_attenuation_db=cam_obs["visual_barrier_db"],
                    visual_source_x=cam_obs["visual_source_x"],
                    visual_source_y=cam_obs["visual_source_y"],
                    visibility_quality=cam_obs["visibility_quality"],
                )

            st = estimator.get_state_summary()
            q_errors.append(abs(st["emission_rate_q"] - gt["true_q"]))
            progress_errors.append(abs(st["progress_pct"] - gt["true_progress"]))

        final_st = estimator.get_state_summary()
        return {
            "name": "Baseline 2: Periodic Scheduled Capture (Fixed T=25) + EKF",
            "q_rmse": float(np.sqrt(np.mean(np.array(q_errors) ** 2))),
            "q_mae": float(np.mean(q_errors)),
            "progress_rmse": float(np.sqrt(np.mean(np.array(progress_errors) ** 2))),
            "captures_required": capture_count,
            "barrier_estimated": final_st["barrier_attenuation_db"],
        }

    def run_baseline_3_greedy_closest(self) -> Dict[str, Any]:
        """
        Baseline 3: EKF active trigger fired, but user snaps from their immediate
        current position rather than navigating to optimal Fisher viewpoint.
        """
        sim = ConstructionSiteSimulator(seed=self.seed)
        estimator = DualRateStateEstimator(dispersion_model=sim.disp)

        q_errors = []
        progress_errors = []
        capture_count = 0
        cooldown = 0
        user_angle = 0.5

        for t in range(self.steps):
            telemetry, gt = sim.step()
            cooldown = max(0, cooldown - 1)

            user_angle += 0.04
            user_x = 55.0 * math.cos(user_angle)
            user_y = 55.0 * math.sin(user_angle)

            estimator.predict(dt=1.0)
            iot_res = estimator.update_iot(
                noise_meas_db=telemetry.noise_db,
                pm25_meas=telemetry.dust_pm25,
                sensor_x=sim.sensor_x,
                sensor_y=sim.sensor_y,
            )

            spatial_var = float(estimator.P[0, 0] + estimator.P[1, 1] + estimator.P[3, 3])
            if cooldown == 0 and (spatial_var > 30.0 or iot_res["residual_norm"] > 22.0):
                capture_count += 1
                cooldown = 20
                # Greedy: snap from immediate current user position looking inward
                cam_obs = sim.simulate_camera_capture(
                    user_x, user_y, math.degrees(math.atan2(-user_y, -user_x))
                )
                estimator.update_visual(
                    visual_progress_pct=cam_obs["visual_progress_pct"],
                    visual_barrier_attenuation_db=cam_obs["visual_barrier_db"],
                    visual_source_x=cam_obs["visual_source_x"],
                    visual_source_y=cam_obs["visual_source_y"],
                    visibility_quality=cam_obs["visibility_quality"],
                )

            st = estimator.get_state_summary()
            q_errors.append(abs(st["emission_rate_q"] - gt["true_q"]))
            progress_errors.append(abs(st["progress_pct"] - gt["true_progress"]))

        final_st = estimator.get_state_summary()
        return {
            "name": "Baseline 3: Greedy Closest Capture + EKF",
            "q_rmse": float(np.sqrt(np.mean(np.array(q_errors) ** 2))),
            "q_mae": float(np.mean(q_errors)),
            "progress_rmse": float(np.sqrt(np.mean(np.array(progress_errors) ** 2))),
            "captures_required": capture_count,
            "barrier_estimated": final_st["barrier_attenuation_db"],
        }

    def run_proposed_dit_doe(self) -> Dict[str, Any]:
        """
        Proposed Method: Dual-Rate Information-Theoretic Directed Observation Engine (DIT-DOE).
        EKF + Fisher Information View-Planning + Closed-Loop Recalibration.
        """
        sim = ConstructionSiteSimulator(seed=self.seed)
        governor = ClosedLoopGovernor(
            sensor_x=sim.sensor_x,
            sensor_y=sim.sensor_y,
            spatial_uncertainty_threshold=30.0,
            residual_trigger_threshold=22.0,
            cooldown_steps=20,
        )

        q_errors = []
        progress_errors = []
        capture_count = 0
        user_angle = 0.5

        for t in range(self.steps):
            telemetry, gt = sim.step()

            user_angle += 0.04
            user_x = 55.0 * math.cos(user_angle)
            user_y = 55.0 * math.sin(user_angle)

            res = governor.process_continuous_telemetry(
                noise_db=telemetry.noise_db,
                pm25=telemetry.dust_pm25,
                current_user_x=user_x,
                current_user_y=user_y,
                dt=1.0,
            )

            # If Fisher Information Engine dispatches an inspection:
            if res["trigger_fired"] and res["action_dispatch"] is not None:
                capture_count += 1
                dispatch = res["action_dispatch"]

                target_x = dispatch["target_x"]
                target_y = dispatch["target_y"]
                target_azimuth = dispatch["target_azimuth_deg"]

                # Capture at optimal Fisher pose (high visibility & direct line-of-sight)
                cam_obs = sim.simulate_camera_capture(
                    camera_x=target_x,
                    camera_y=target_y,
                    camera_azimuth_deg=target_azimuth,
                )

                governor.process_episodic_visual(
                    visual_progress_pct=cam_obs["visual_progress_pct"],
                    visual_barrier_attenuation_db=cam_obs["visual_barrier_db"],
                    camera_x=target_x,
                    camera_y=target_y,
                    camera_azimuth_deg=target_azimuth,
                    visual_source_x=cam_obs["visual_source_x"],
                    visual_source_y=cam_obs["visual_source_y"],
                    visibility_quality=cam_obs["visibility_quality"],
                )

            st = governor.estimator.get_state_summary()
            q_errors.append(abs(st["emission_rate_q"] - gt["true_q"]))
            progress_errors.append(abs(st["progress_pct"] - gt["true_progress"]))

        final_st = governor.estimator.get_state_summary()
        return {
            "name": "Proposed Method: DIT-DOE (Closed-Loop Fisher Perception)",
            "q_rmse": float(np.sqrt(np.mean(np.array(q_errors) ** 2))),
            "q_mae": float(np.mean(q_errors)),
            "progress_rmse": float(np.sqrt(np.mean(np.array(progress_errors) ** 2))),
            "captures_required": capture_count,
            "barrier_estimated": final_st["barrier_attenuation_db"],
            "true_barrier_db": sim.true_barrier_db,
        }
