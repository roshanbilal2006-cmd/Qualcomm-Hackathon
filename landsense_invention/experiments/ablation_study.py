"""
LandSense Invention: Component Ablation Study
Module: landsense_invention.experiments.ablation_study

Isolates the technical contribution of each component to prove INVENTIVE STEP:
- Full DIT-DOE (EKF + Barrier Physics + Fisher View Planning + Recalibration)
- Ablation A: No Physical Barrier Model (assumes free-field A_barrier = 0)
- Ablation B: No Information View-Planning (random viewing angles)
- Ablation C: Open-Loop (no feedback recalibration of IoT transfer function)
"""

import os
import json
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List

from landsense_invention.simulation.site_simulator import ConstructionSiteSimulator
from landsense_invention.controller.closed_loop_governor import ClosedLoopGovernor
from landsense_invention.controller.state_estimator import DualRateStateEstimator


class AblationSuite:
    def __init__(self, steps: int = 120, seeds: List[int] = [42, 101, 202, 303, 404]):
        self.steps = steps
        self.seeds = seeds

    def run_ablation_a_no_barrier_model(self, seed: int) -> Dict[str, Any]:
        """Ablation A: State estimator has no concept of barrier insertion loss."""
        sim = ConstructionSiteSimulator(seed=seed)
        estimator = DualRateStateEstimator(dispersion_model=sim.disp)
        # Force barrier attenuation to zero permanently
        estimator.x[3] = 0.0
        estimator.P[3, 3] = 0.0
        estimator.Q_proc[3, 3] = 0.0

        q_errors = []
        user_angle = 0.5

        for t in range(self.steps):
            telemetry, gt = sim.step()
            user_angle += 0.04
            user_x = 55.0 * np.cos(user_angle)
            user_y = 55.0 * np.sin(user_angle)

            estimator.predict(dt=1.0)
            estimator.x[3] = 0.0  # clamp to 0
            estimator.update_iot(telemetry.noise_db, telemetry.dust_pm25, sim.sensor_x, sim.sensor_y)
            estimator.x[3] = 0.0

            # Snap photo every 30 steps
            if (t + 1) % 30 == 0:
                cam = sim.simulate_camera_capture(user_x, user_y, np.degrees(np.arctan2(-user_y, -user_x)))
                estimator.update_visual(cam["visual_progress_pct"], 0.0, cam["visual_source_x"], cam["visual_source_y"], cam["visibility_quality"])
                estimator.x[3] = 0.0

            st = estimator.get_state_summary()
            q_errors.append(abs(st["emission_rate_q"] - gt["true_q"]))

        return {"q_rmse": float(np.sqrt(np.mean(np.array(q_errors) ** 2)))}

    def run_ablation_b_no_view_planning(self, seed: int) -> Dict[str, Any]:
        """Ablation B: EKF has barrier model, but captures photos at random angles without Fisher Information."""
        sim = ConstructionSiteSimulator(seed=seed)
        estimator = DualRateStateEstimator(dispersion_model=sim.disp)
        np.random.seed(seed)

        q_errors = []
        user_angle = 0.5
        cooldown = 0

        for t in range(self.steps):
            telemetry, gt = sim.step()
            cooldown = max(0, cooldown - 1)
            user_angle += 0.04
            user_x = 55.0 * np.cos(user_angle)
            user_y = 55.0 * np.sin(user_angle)

            estimator.predict(dt=1.0)
            iot_res = estimator.update_iot(telemetry.noise_db, telemetry.dust_pm25, sim.sensor_x, sim.sensor_y)

            spatial_var = float(estimator.P[0, 0] + estimator.P[1, 1] + estimator.P[3, 3])
            if cooldown == 0 and (spatial_var > 30.0 or iot_res["residual_norm"] > 22.0):
                cooldown = 20
                # Random unguided viewing angle and random point
                rand_ang = float(np.random.uniform(0, 2 * np.pi))
                rx = 55.0 * np.cos(rand_ang)
                ry = 55.0 * np.sin(rand_ang)
                cam = sim.simulate_camera_capture(rx, ry, float(np.random.uniform(0, 360)))
                estimator.update_visual(cam["visual_progress_pct"], cam["visual_barrier_db"], cam["visual_source_x"], cam["visual_source_y"], cam["visibility_quality"])

            st = estimator.get_state_summary()
            q_errors.append(abs(st["emission_rate_q"] - gt["true_q"]))

        return {"q_rmse": float(np.sqrt(np.mean(np.array(q_errors) ** 2)))}

    def run_ablation_c_no_recalibration(self, seed: int) -> Dict[str, Any]:
        """Ablation C: Visual frames are captured, but NOT used to update barrier attenuation parameter."""
        sim = ConstructionSiteSimulator(seed=seed)
        governor = ClosedLoopGovernor(sensor_x=sim.sensor_x, sensor_y=sim.sensor_y)

        q_errors = []
        user_angle = 0.5

        for t in range(self.steps):
            telemetry, gt = sim.step()
            user_angle += 0.04
            user_x = 55.0 * np.cos(user_angle)
            user_y = 55.0 * np.sin(user_angle)

            res = governor.process_continuous_telemetry(telemetry.noise_db, telemetry.dust_pm25, user_x, user_y, dt=1.0)
            if res["trigger_fired"] and res["action_dispatch"] is not None:
                d = res["action_dispatch"]
                cam = sim.simulate_camera_capture(d["target_x"], d["target_y"], d["target_azimuth_deg"])
                # Open loop: do NOT update barrier in estimator (leave at initial guess 5.0 dB)
                governor.process_episodic_visual(
                    visual_progress_pct=cam["visual_progress_pct"],
                    visual_barrier_attenuation_db=5.0,  # locked at incorrect prior
                    camera_x=d["target_x"],
                    camera_y=d["target_y"],
                    camera_azimuth_deg=d["target_azimuth_deg"],
                    visual_source_x=cam["visual_source_x"],
                    visual_source_y=cam["visual_source_y"],
                    visibility_quality=cam["visibility_quality"],
                )

            st = governor.estimator.get_state_summary()
            q_errors.append(abs(st["emission_rate_q"] - gt["true_q"]))

        return {"q_rmse": float(np.sqrt(np.mean(np.array(q_errors) ** 2)))}

    def run_full_suite(self) -> Dict[str, Any]:
        results = {"full_dit_doe": [], "ablation_a_no_barrier": [], "ablation_b_no_view_plan": [], "ablation_c_no_recalibration": []}

        for s in self.seeds:
            # Full DIT-DOE
            sim = ConstructionSiteSimulator(seed=s)
            gov = ClosedLoopGovernor(sensor_x=sim.sensor_x, sensor_y=sim.sensor_y)
            u_ang = 0.5
            q_errs = []
            for t in range(self.steps):
                tel, gt = sim.step()
                u_ang += 0.04
                ux = 55.0 * np.cos(u_ang)
                uy = 55.0 * np.sin(u_ang)
                res = gov.process_continuous_telemetry(tel.noise_db, tel.dust_pm25, ux, uy, dt=1.0)
                if res["trigger_fired"] and res["action_dispatch"]:
                    d = res["action_dispatch"]
                    cam = sim.simulate_camera_capture(d["target_x"], d["target_y"], d["target_azimuth_deg"])
                    gov.process_episodic_visual(cam["visual_progress_pct"], cam["visual_barrier_db"], d["target_x"], d["target_y"], d["target_azimuth_deg"], cam["visual_source_x"], cam["visual_source_y"], cam["visibility_quality"])
                st = gov.estimator.get_state_summary()
                q_errs.append(abs(st["emission_rate_q"] - gt["true_q"]))

            results["full_dit_doe"].append(float(np.sqrt(np.mean(np.array(q_errs) ** 2))))
            results["ablation_a_no_barrier"].append(self.run_ablation_a_no_barrier_model(s)["q_rmse"])
            results["ablation_b_no_view_plan"].append(self.run_ablation_b_no_view_planning(s)["q_rmse"])
            results["ablation_c_no_recalibration"].append(self.run_ablation_c_no_recalibration(s)["q_rmse"])

        summary = {
            k: {
                "mean_rmse": float(np.mean(v)),
                "std_rmse": float(np.std(v)),
            }
            for k, v in results.items()
        }

        os.makedirs("landsense_invention/results", exist_ok=True)
        with open("landsense_invention/results/ablation_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary


if __name__ == "__main__":
    suite = AblationSuite()
    out = suite.run_full_suite()
    print("================== ABLATION STUDY RESULTS ==================")
    for k, v in out.items():
        print(f"{k:35s}: {v['mean_rmse']:.2f} +/- {v['std_rmse']:.2f} ug/s")
    print("============================================================")
