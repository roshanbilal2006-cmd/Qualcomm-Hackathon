"""
LandSense Invention: Fisher Information View-Planning Engine
Module: landsense_invention.controller.information_engine

Evaluates candidate inspection poses (x, y, azimuth) along site boundaries
to maximize the Fisher Information Gain / D-optimality criterion,
resolving latent spatial ambiguity and barrier parameters with minimum human travel.
"""

import math
import numpy as np
from typing import List, Tuple, Dict, Any, Optional


class FisherInformationEngine:
    """
    Computes optimal observation waypoints by evaluating the Fisher Information
    Matrix (FIM) over candidate boundary inspection poses.
    """

    def __init__(
        self,
        site_radius_m: float = 50.0,
        candidate_count: int = 16,
        r_visual_base: float = 3.0,
    ):
        self.site_radius = site_radius_m
        self.candidate_count = candidate_count
        self.r_visual_base = r_visual_base
        self.candidates = self._generate_boundary_candidates()

    def _generate_boundary_candidates(self) -> List[Tuple[float, float, float]]:
        """
        Generates candidate inspection waypoints around accessible perimeter.
        Returns list of (x, y, viewing_azimuth_rad).
        """
        candidates = []
        for i in range(self.candidate_count):
            angle = (2.0 * math.pi * i) / self.candidate_count
            # Place candidate on perimeter perimeter road/sidewalk (1.1 * site_radius)
            x = (self.site_radius * 1.1) * math.cos(angle)
            y = (self.site_radius * 1.1) * math.sin(angle)
            # Inward pointing azimuth towards center (rad)
            azimuth = math.atan2(-y, -x)
            candidates.append((x, y, azimuth))
        return candidates

    def compute_fisher_information(
        self,
        candidate_pose: Tuple[float, float, float],
        estimated_source_x: float,
        estimated_source_y: float,
        prior_covariance: np.ndarray,
    ) -> float:
        """
        Evaluates the information metric for a candidate pose:
        Score = log(det(P_prior^-1 + FIM(pose))) - distance_penalty
        """
        cand_x, cand_y, cand_azimuth = candidate_pose

        # Vector from camera to estimated source
        dx = estimated_source_x - cand_x
        dy = estimated_source_y - cand_y
        dist = math.sqrt(dx * dx + dy * dy)
        dist = max(1.0, dist)

        angle_to_source = math.atan2(dy, dx)
        # Angular deviation between camera pointing azimuth and true line of sight
        angle_diff = abs((cand_azimuth - angle_to_source + math.pi) % (2.0 * math.pi) - math.pi)

        # Field-of-View attenuation factor: best visibility within +/- 45 degrees
        fov_coverage = max(0.05, math.cos(min(math.pi * 0.45, angle_diff)))

        # Distance attenuation: closer cameras achieve higher visual SNR (1/dist)
        spatial_snr = (self.site_radius / dist) * fov_coverage

        # Construct synthetic Observation Jacobian for this viewpoint H_v(p)
        # Observing [barrier, progress, source_x, source_y]
        # Cross-angle geometry: viewpoints perpendicular to current uncertainty
        # major axis yield highest localization gain
        H_cand = np.zeros((4, 5))
        H_cand[0, 3] = 1.0 * fov_coverage             # barrier observability
        H_cand[1, 4] = 1.0 * fov_coverage             # progress observability
        H_cand[2, 0] = math.cos(angle_to_source) * spatial_snr  # x projection
        H_cand[3, 1] = math.sin(angle_to_source) * spatial_snr  # y projection

        R_inv = np.diag([
            1.0 / (2.0 ** 2),
            1.0 / (4.0 ** 2),
            1.0 / (max(1.0, 5.0 / spatial_snr) ** 2),
            1.0 / (max(1.0, 5.0 / spatial_snr) ** 2),
        ])

        # Fisher Information Matrix F = H^T R^-1 H
        FIM = H_cand.T @ R_inv @ H_cand

        # Posterior precision matrix = P^-1 + FIM
        try:
            P_inv = np.linalg.inv(prior_covariance)
            P_post_inv = P_inv + FIM
            # D-optimality log-determinant (higher is better)
            sign, logdet = np.linalg.slogdet(P_post_inv)
            info_gain = float(logdet) if sign > 0 else 0.0
        except np.linalg.LinAlgError:
            info_gain = float(np.trace(FIM))

        return info_gain

    def select_optimal_waypoint(
        self,
        current_user_x: float,
        current_user_y: float,
        estimated_source_x: float,
        estimated_source_y: float,
        prior_covariance: np.ndarray,
        travel_cost_weight: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Selects the candidate waypoint that maximizes Information Gain
        minus travel cost from current user position.
        """
        best_score = -float("inf")
        best_candidate = self.candidates[0]
        scored_candidates = []

        for cand in self.candidates:
            cx, cy, caz = cand
            info_val = self.compute_fisher_information(
                cand, estimated_source_x, estimated_source_y, prior_covariance
            )
            # Travel distance penalty
            travel_dist = math.sqrt((cx - current_user_x) ** 2 + (cy - current_user_y) ** 2)
            net_score = info_val - travel_cost_weight * travel_dist

            scored_candidates.append({
                "x": round(cx, 1),
                "y": round(cy, 1),
                "azimuth_deg": round(math.degrees(caz), 1),
                "info_metric": round(info_val, 2),
                "travel_distance_m": round(travel_dist, 1),
                "net_score": round(net_score, 2),
            })

            if net_score > best_score:
                best_score = net_score
                best_candidate = cand

        return {
            "optimal_x": round(best_candidate[0], 2),
            "optimal_y": round(best_candidate[1], 2),
            "optimal_azimuth_deg": round(math.degrees(best_candidate[2]), 1),
            "best_score": round(best_score, 2),
            "all_candidates": scored_candidates,
        }
