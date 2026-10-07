"""
LandSense Invention: Physical Sensing & Telemetry Model
Module: landsense_invention.sensing.telemetry_model

Models the physical acoustic sound pressure propagation (inverse-square law
with barrier insertion loss) and 2D atmospheric advection-diffusion particulate
dispersion across urban construction boundaries.
"""

import math
import numpy as np
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any


@dataclass
class EnvironmentalTelemetry:
    timestamp: float
    noise_db: float
    dust_pm25: float
    dust_pm10: float
    sensor_id: str
    sensor_x: float
    sensor_y: float
    raw_status: str = "ok"


class PhysicalDispersionModel:
    """
    Physically grounded forward model for acoustic sound pressure and
    particulate dispersion around an urban construction site.
    """

    def __init__(
        self,
        ambient_noise_db: float = 55.0,
        ambient_pm25: float = 25.0,
        ambient_pm10: float = 45.0,
        wind_speed_m_s: float = 2.5,
        wind_direction_rad: float = 0.0,  # 0 = blowing East (+x)
        eddy_diffusivity: float = 1.2,
    ):
        self.ambient_noise_db = ambient_noise_db
        self.ambient_pm25 = ambient_pm25
        self.ambient_pm10 = ambient_pm10
        self.wind_speed = max(0.2, wind_speed_m_s)
        self.wind_direction = wind_direction_rad
        self.K_diff = eddy_diffusivity

    def compute_acoustic_spl(
        self,
        source_x: float,
        source_y: float,
        source_sound_power_lw: float,
        sensor_x: float,
        sensor_y: float,
        barrier_attenuation_db: float = 0.0,
        air_absorption_coeff: float = 0.005,
    ) -> float:
        """
        Computes Sound Pressure Level (SPL in dBA) at sensor position.
        ISO 9613-2 propagation model:
        Lp = Lw - 20*log10(r) - 11 - A_barrier - A_air + ambient
        """
        dx = sensor_x - source_x
        dy = sensor_y - source_y
        dist = math.sqrt(dx * dx + dy * dy)
        dist = max(1.0, dist)  # avoid division by zero in near-field

        # Geometric divergence (spherical spreading in free half-space)
        geom_div = 20.0 * math.log10(dist) + 11.0
        air_abs = air_absorption_coeff * dist
        barrier_loss = max(0.0, barrier_attenuation_db)

        # Received SPL from construction source
        direct_spl = source_sound_power_lw - geom_div - barrier_loss - air_abs
        direct_spl = max(0.0, direct_spl)

        # Logarithmic acoustic summation with ambient background noise
        p_source = 10.0 ** (direct_spl / 10.0)
        p_ambient = 10.0 ** (self.ambient_noise_db / 10.0)
        total_spl = 10.0 * math.log10(p_source + p_ambient)

        return float(round(total_spl, 2))

    def compute_particulate_concentration(
        self,
        source_x: float,
        source_y: float,
        emission_rate_q: float,  # ug/s
        sensor_x: float,
        sensor_y: float,
        barrier_filtration_efficiency: float = 0.0,  # 0.0 to 0.8
    ) -> Tuple[float, float]:
        """
        Computes PM2.5 and PM10 concentrations using a steady-state 2D
        Gaussian plume advection-diffusion approximation with wind vector.
        """
        dx = sensor_x - source_x
        dy = sensor_y - source_y

        # Rotate coordinates into wind-aligned frame
        # downwind: parallel to wind; crosswind: perpendicular
        cos_w = math.cos(self.wind_direction)
        sin_w = math.sin(self.wind_direction)
        x_downwind = dx * cos_w + dy * sin_w
        y_crosswind = -dx * sin_w + dy * cos_w

        # If sensor is upwind of source, minimal turbulent back-diffusion occurs
        if x_downwind <= 0:
            upwind_dist = abs(x_downwind)
            back_diff = math.exp(-upwind_dist / (2.0 * self.K_diff))
            plume_conc = (emission_rate_q / (2.0 * math.pi * self.K_diff * 10.0)) * back_diff
        else:
            # Dispersion coefficients expanding downwind
            sigma_y = max(1.0, 0.35 * (x_downwind ** 0.85) + self.K_diff)
            sigma_z = max(1.0, 0.25 * (x_downwind ** 0.80) + 1.5)

            # Plume concentration at surface (ground reflection factor 2)
            denom = 2.0 * math.pi * self.wind_speed * sigma_y * sigma_z
            crosswind_term = math.exp(-(y_crosswind ** 2) / (2.0 * sigma_y ** 2))
            plume_conc = (emission_rate_q / denom) * crosswind_term

        # Barrier filtration effect
        plume_conc = plume_conc * (1.0 - min(0.9, barrier_filtration_efficiency))

        # Separate into PM2.5 (fine fraction ~35%) and PM10 (total particulate ~100%)
        pm25 = self.ambient_pm25 + 0.35 * plume_conc
        pm10 = self.ambient_pm10 + plume_conc

        return float(round(pm25, 2)), float(round(pm10, 2))
