"""
LandSense Invention: Kill-Test Experiment Runner & Validation Suite
Module: landsense_invention.experiments.kill_test_runner

Runs multi-seed Monte Carlo comparative benchmarks across Baseline 0, 1, 2, 3
and Proposed (DIT-DOE). Evaluates formal kill conditions and persists evidence.
"""

import os
import json
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List

from landsense_invention.experiments.baselines import BaselineRunner


def run_full_kill_test_battery(
    seeds: List[int] = [42, 101, 202, 303, 404],
    steps_per_run: int = 120,
    output_dir: str = "landsense_invention/results",
) -> Dict[str, Any]:
    """
    Executes the definitive kill-test across multiple random seeds.
    Computes means, standard deviations, and checks kill test pass/fail conditions.
    """
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("landsense_invention/evidence", exist_ok=True)

    methods = [
        "baseline_0_current",
        "baseline_1_threshold",
        "baseline_2_periodic",
        "baseline_3_greedy",
        "proposed_dit_doe",
    ]

    aggregated: Dict[str, Dict[str, List[float]]] = {
        m: {
            "q_rmse": [],
            "q_mae": [],
            "progress_rmse": [],
            "captures": [],
            "barrier_err": [],
        }
        for m in methods
    }

    print("================================================================================")
    print("STARTING LANDSENSE INVENTION DECISIVE KILL-TEST BATTERY")
    print(f"Seeds: {seeds} | Steps per seed: {steps_per_run}")
    print("================================================================================")

    for seed in seeds:
        runner = BaselineRunner(steps=steps_per_run, seed=seed)

        # Run all methods
        b0 = runner.run_baseline_0_current_landsense()
        b1 = runner.run_baseline_1_threshold_heuristic()
        b2 = runner.run_baseline_2_periodic_scheduled()
        b3 = runner.run_baseline_3_greedy_closest()
        prop = runner.run_proposed_dit_doe()

        # Collect metrics
        aggregated["baseline_0_current"]["q_rmse"].append(b0["q_rmse"])
        aggregated["baseline_0_current"]["q_mae"].append(b0["q_mae"])
        aggregated["baseline_0_current"]["progress_rmse"].append(b0["progress_rmse"])
        aggregated["baseline_0_current"]["captures"].append(b0["captures_required"])

        aggregated["baseline_1_threshold"]["q_rmse"].append(b1["q_rmse"])
        aggregated["baseline_1_threshold"]["q_mae"].append(b1["q_mae"])
        aggregated["baseline_1_threshold"]["progress_rmse"].append(b1["progress_rmse"])
        aggregated["baseline_1_threshold"]["captures"].append(b1["captures_required"])

        aggregated["baseline_2_periodic"]["q_rmse"].append(b2["q_rmse"])
        aggregated["baseline_2_periodic"]["q_mae"].append(b2["q_mae"])
        aggregated["baseline_2_periodic"]["progress_rmse"].append(b2["progress_rmse"])
        aggregated["baseline_2_periodic"]["captures"].append(b2["captures_required"])
        if b2["barrier_estimated"] is not None:
            aggregated["baseline_2_periodic"]["barrier_err"].append(abs(b2["barrier_estimated"] - 12.5))

        aggregated["baseline_3_greedy"]["q_rmse"].append(b3["q_rmse"])
        aggregated["baseline_3_greedy"]["q_mae"].append(b3["q_mae"])
        aggregated["baseline_3_greedy"]["progress_rmse"].append(b3["progress_rmse"])
        aggregated["baseline_3_greedy"]["captures"].append(b3["captures_required"])
        if b3["barrier_estimated"] is not None:
            aggregated["baseline_3_greedy"]["barrier_err"].append(abs(b3["barrier_estimated"] - 12.5))

        aggregated["proposed_dit_doe"]["q_rmse"].append(prop["q_rmse"])
        aggregated["proposed_dit_doe"]["q_mae"].append(prop["q_mae"])
        aggregated["proposed_dit_doe"]["progress_rmse"].append(prop["progress_rmse"])
        aggregated["proposed_dit_doe"]["captures"].append(prop["captures_required"])
        if prop["barrier_estimated"] is not None:
            aggregated["proposed_dit_doe"]["barrier_err"].append(abs(prop["barrier_estimated"] - 12.5))

    # Compute summary statistics (Mean +/- Std)
    summary_results: Dict[str, Dict[str, Any]] = {}
    for m in methods:
        summary_results[m] = {
            "q_rmse_mean": float(np.mean(aggregated[m]["q_rmse"])),
            "q_rmse_std": float(np.std(aggregated[m]["q_rmse"])),
            "q_mae_mean": float(np.mean(aggregated[m]["q_mae"])),
            "q_mae_std": float(np.std(aggregated[m]["q_mae"])),
            "progress_rmse_mean": float(np.mean(aggregated[m]["progress_rmse"])),
            "captures_mean": float(np.mean(aggregated[m]["captures"])),
            "barrier_err_mean": float(np.mean(aggregated[m]["barrier_err"])) if aggregated[m]["barrier_err"] else None,
        }

    # Evaluate Kill-Test Criteria
    prop_q_rmse = summary_results["proposed_dit_doe"]["q_rmse_mean"]
    b0_q_rmse = summary_results["baseline_0_current"]["q_rmse_mean"]
    b1_q_rmse = summary_results["baseline_1_threshold"]["q_rmse_mean"]
    b2_q_rmse = summary_results["baseline_2_periodic"]["q_rmse_mean"]
    b3_q_rmse = summary_results["baseline_3_greedy"]["q_rmse_mean"]

    prop_caps = summary_results["proposed_dit_doe"]["captures_mean"]
    b2_caps = summary_results["baseline_2_periodic"]["captures_mean"]

    prop_barrier_err = summary_results["proposed_dit_doe"]["barrier_err_mean"]

    # Criterion 1: >40% improvement in Q RMSE over Baseline 0
    c1_reduction_b0 = 100.0 * (1.0 - (prop_q_rmse / b0_q_rmse))
    c1_pass = c1_reduction_b0 >= 40.0

    # Criterion 2: Better accuracy than Periodic Baseline 2 while requiring <= captures
    c2_pass = (prop_q_rmse < b2_q_rmse) and (prop_caps <= b2_caps)

    # Criterion 3: Outperforms Baseline 3 (Greedy) due to Fisher Information view-planning
    c3_pass = (prop_q_rmse < b3_q_rmse) and (summary_results["proposed_dit_doe"]["progress_rmse_mean"] <= summary_results["baseline_3_greedy"]["progress_rmse_mean"])

    # Criterion 4: Converges on true physical barrier attenuation within 2.5 dB
    c4_pass = prop_barrier_err is not None and prop_barrier_err <= 2.5

    all_criteria_met = c1_pass and c2_pass and c3_pass and c4_pass
    overall_status = "SURVIVED (PROVEN ADVANTAGE)" if all_criteria_met else "KILLED (HYPOTHESIS REJECTED)"

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "overall_status": overall_status,
        "criteria": {
            "C1_reduction_over_current_pct": round(c1_reduction_b0, 1),
            "C1_pass": bool(c1_pass),
            "C2_beats_periodic_with_fewer_captures": bool(c2_pass),
            "C3_beats_greedy_closest": bool(c3_pass),
            "C4_barrier_recalibration_error_db": round(prop_barrier_err, 2) if prop_barrier_err else None,
            "C4_pass": bool(c4_pass),
        },
        "summary_table": summary_results,
    }

    # Save to results directory
    out_path = os.path.join(output_dir, "kill_test_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n----------------- KILL TEST EVALUATION SUMMARY -----------------")
    print(f"Overall Status:                   {overall_status}")
    print(f"Emission Error Reduction vs B0:   {c1_reduction_b0:.1f}% (Pass: {c1_pass})")
    print(f"Captures Demanded (Prop vs B2):   {prop_caps:.1f} vs {b2_caps:.1f} (Pass: {c2_pass})")
    print(f"Barrier Estimation Error:         {prop_barrier_err:.2f} dB (Pass: {c4_pass})")
    print(f"Results persisted to:             {out_path}")
    print("----------------------------------------------------------------\n")

    return report


if __name__ == "__main__":
    run_full_kill_test_battery()
