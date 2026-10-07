"""
Backend Adapter: LandSense Cyber-Physical Invention (DIT-DOE)
Module: backend.adapters.invention_adapter

Provides a seamless, turnkey bridge connecting the backend pipeline/orchestrator
to the patented ClosedLoopGovernor state estimator.
"""

import logging
from typing import Dict, Any, Optional

from landsense_invention.controller.closed_loop_governor import ClosedLoopGovernor
from landsense_invention.sensing.physical_coupling import compute_shared_transport_parameters

logger = logging.getLogger("landsense.invention_adapter")


class InventionAdapter:
    """
    Adapter bridging backend microservices to the patented DIT-DOE governor.
    Maintains continuous cyber-physical state estimation (source location,
    emission rate, barrier structural attenuation).
    """

    _instance: Optional["InventionAdapter"] = None

    def __init__(
        self,
        sensor_x: float = 0.0,
        sensor_y: float = 55.0,
        site_radius_m: float = 50.0,
    ):
        self.governor = ClosedLoopGovernor(
            sensor_x=sensor_x,
            sensor_y=sensor_y,
            site_radius_m=site_radius_m,
        )
        logger.info(
            f"Initialized LandSense DIT-DOE InventionAdapter with boundary sensor at ({sensor_x}, {sensor_y})"
        )

    @classmethod
    def get_instance(cls) -> "InventionAdapter":
        """Singleton accessor for application-wide state persistence."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def process_telemetry(
        self,
        noise_db: float,
        pm25: float,
        current_user_x: float = 0.0,
        current_user_y: float = 0.0,
        dt: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Ingests continuous 1Hz IoT sensor readings (noise dBA and dust PM2.5).
        Returns current state estimate and any active inspection dispatch instruction.
        """
        try:
            return self.governor.process_continuous_telemetry(
                noise_db=noise_db,
                pm25=pm25,
                current_user_x=current_user_x,
                current_user_y=current_user_y,
                dt=dt,
            )
        except Exception as e:
            logger.error(f"InventionAdapter telemetry error: {e}", exc_info=True)
            return {
                "step": self.governor.step_counter,
                "error": str(e),
                "state_estimate": self.governor.estimator.get_state_summary(),
                "trigger_fired": False,
                "action_dispatch": None,
            }

    def process_visual_observation(
        self,
        visual_progress_pct: float,
        barrier_height_m: float = 2.4,
        barrier_solidity: float = 0.95,
        camera_x: float = 0.0,
        camera_y: float = 50.0,
        camera_azimuth_deg: float = 180.0,
    ) -> Dict[str, Any]:
        """
        Ingests mobile optical photo evidence. Computes shared physical barrier
        attenuation via Maekawa diffraction and Raupach aerodynamic shelter,
        then collapses filter covariance.
        """
        try:
            # Physical coupling
            a_db, eta_dust = compute_shared_transport_parameters(
                effective_height_m=barrier_height_m,
                solidity_ratio=barrier_solidity,
                source_dist_m=15.0,
                sensor_dist_m=55.0,
            )

            vis_result = self.governor.process_episodic_visual(
                visual_progress_pct=visual_progress_pct,
                visual_barrier_attenuation_db=a_db,
                camera_x=camera_x,
                camera_y=camera_y,
                camera_azimuth_deg=camera_azimuth_deg,
            )
            vis_result["computed_barrier_insertion_loss_db"] = a_db
            vis_result["computed_dust_shelter_retention"] = eta_dust
            return vis_result
        except Exception as e:
            logger.error(f"InventionAdapter visual processing error: {e}", exc_info=True)
            return {"error": str(e), "state_estimate": self.governor.estimator.get_state_summary()}

    def get_state_summary(self) -> Dict[str, Any]:
        """Returns the current estimated state vector and uncertainty."""
        summary = self.governor.estimator.get_state_summary()
        summary["total_dispatches"] = self.governor.total_dispatches
        summary["total_visual_updates"] = self.governor.total_visual_updates
        return summary
