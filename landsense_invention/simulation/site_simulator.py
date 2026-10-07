"""
LandSense Invention: Physical Site Ground-Truth Simulator - Refined
Module: landsense_invention.simulation.site_simulator

Generates ground-truth construction dynamics, machinery duty cycles,
barrier attenuation, wind turbulence, and geometry-dependent camera capture.
"""

import math
import random
import numpy as np
from typing import Dict, Any, Tuple
from landsense_invention.sensing.telemetry_model import PhysicalDispersionModel, EnvironmentalTelemetry


class ConstructionSiteSimulator:
    """
    Simulates a ground-truth physical construction site with non-stationary
    emission events, physical perimeter barrier occlusions, and sensor noise.
    """

    def __init__(
        self,
        true_source_x: float = 12.0,
        true_source_y: float = -10.0,
        true_barrier_attenuation_db: float = 12.5,  # physical sheet metal boundary wall
        true_initial_progress_pct: float = 38.0,
        sensor_x: float = 0.0,
        sensor_y: float = 55.0,  # boundary node at North perimeter
        wind_speed_m_s: float = 2.8,
        wind_direction_rad: float = math.radians(45.0), # blowing North-East
        seed: int = 42,
    ):
        random.seed(seed)
        np.random.seed(seed)

        self.true_x_s = true_source_x
        self.true_y_s = true_source_y
        self.true_barrier_db = true_barrier_attenuation_db
        self.true_progress = true_initial_progress_pct
        self.sensor_x = sensor_x
        self.sensor_y = sensor_y

        self.disp = PhysicalDispersionModel(
            wind_speed_m_s=wind_speed_m_s,
            wind_direction_rad=wind_direction_rad,
        )

        self.time_step = 0
        self.machinery_state = "IDLE"

    def step(self) -> Tuple[EnvironmentalTelemetry, Dict[str, Any]]:
        self.time_step += 1

        # Burst events occur periodically (e.g. heavy excavation or rock breaking)
        cycle = self.time_step % 60
        if cycle < 20:
            self.machinery_state = "IDLE"
            base_q = 80.0
            sound_power_lw = 70.0
        elif cycle < 45:
            self.machinery_state = "EXCAVATING"
            base_q = 650.0
            sound_power_lw = 96.0
        else:
            self.machinery_state = "ROCK_BREAKING"
            base_q = 1200.0
            sound_power_lw = 104.0

        true_q = max(20.0, base_q + float(np.random.normal(0, 35.0)))
        true_lw = max(60.0, sound_power_lw + float(np.random.normal(0, 1.0)))

        if self.machinery_state != "IDLE":
            self.true_progress = min(100.0, self.true_progress + 0.015)

        clean_spl = self.disp.compute_acoustic_spl(
            source_x=self.true_x_s,
            source_y=self.true_y_s,
            source_sound_power_lw=true_lw,
            sensor_x=self.sensor_x,
            sensor_y=self.sensor_y,
            barrier_attenuation_db=self.true_barrier_db,
        )

        barrier_dust_filt = min(0.8, self.true_barrier_db * 0.04)
        clean_pm25, clean_pm10 = self.disp.compute_particulate_concentration(
            source_x=self.true_x_s,
            source_y=self.true_y_s,
            emission_rate_q=true_q,
            sensor_x=self.sensor_x,
            sensor_y=self.sensor_y,
            barrier_filtration_efficiency=barrier_dust_filt,
        )

        noise_meas = clean_spl + float(np.random.normal(0, 1.5))
        pm25_meas = max(5.0, clean_pm25 + float(np.random.normal(0, 3.5)))
        pm10_meas = max(10.0, clean_pm10 + float(np.random.normal(0, 6.0)))

        telemetry = EnvironmentalTelemetry(
            timestamp=float(self.time_step),
            noise_db=round(noise_meas, 1),
            dust_pm25=round(pm25_meas, 1),
            dust_pm10=round(pm10_meas, 1),
            sensor_id="UNO-Q-BOUNDARY",
            sensor_x=self.sensor_x,
            sensor_y=self.sensor_y,
        )

        ground_truth = {
            "step": self.time_step,
            "machinery_state": self.machinery_state,
            "true_q": round(float(true_q), 1),
            "true_lw": round(float(true_lw), 1),
            "true_barrier_db": round(float(self.true_barrier_db), 2),
            "true_progress": round(float(self.true_progress), 2),
            "true_source_x": self.true_x_s,
            "true_source_y": self.true_y_s,
            "clean_spl": clean_spl,
            "clean_pm25": clean_pm25,
        }

        return telemetry, ground_truth

    def simulate_camera_capture(
        self,
        camera_x: float,
        camera_y: float,
        camera_azimuth_deg: float,
    ) -> Dict[str, Any]:
        """
        Simulates mobile visual capture at given coordinates and azimuth.
        Quality and triangulated accuracy depend directly on line-of-sight geometry.
        """
        dx = self.true_x_s - camera_x
        dy = self.true_y_s - camera_y
        dist = math.sqrt(dx * dx + dy * dy)

        true_angle = math.degrees(math.atan2(dy, dx))
        azimuth_err = abs((camera_azimuth_deg - true_angle + 180.0) % 360.0 - 180.0)

        # Direct line-of-sight score: highest when close and pointing straight at site
        fov_factor = max(0.05, math.cos(math.radians(min(85.0, azimuth_err))))
        dist_factor = min(1.0, 45.0 / max(15.0, dist))
        visibility = fov_factor * dist_factor
        visibility = max(0.1, min(1.0, visibility))

        # Measurement noise scales inversely with visibility
        barrier_err = float(np.random.normal(0, max(0.3, 2.5 * (1.0 - visibility))))
        progress_err = float(np.random.normal(0, max(0.8, 5.0 * (1.0 - visibility))))
        pos_err_x = float(np.random.normal(0, max(0.8, 6.0 * (1.0 - visibility))))
        pos_err_y = float(np.random.normal(0, max(0.8, 6.0 * (1.0 - visibility))))

        obs_barrier_db = max(0.0, min(25.0, self.true_barrier_db + barrier_err))
        obs_progress_pct = max(0.0, min(100.0, self.true_progress + progress_err))
        obs_source_x = self.true_x_s + pos_err_x
        obs_source_y = self.true_y_s + pos_err_y

        return {
            "visual_barrier_db": round(obs_barrier_db, 2),
            "visual_progress_pct": round(obs_progress_pct, 1),
            "visual_source_x": round(obs_source_x, 2),
            "visual_source_y": round(obs_source_y, 2),
            "visibility_quality": round(visibility, 2),
            "camera_dist_to_source": round(dist, 1),
            "camera_azimuth_err_deg": round(azimuth_err, 1),
        }
