import logging

logger = logging.getLogger("landsense.scoring")

def calculate_development_score(
    visual_stage: str,
    progress: float,
    visual_confidence: float,
    sensor_status: str,
    noise_db: float | None,
    dust_pm25: float | None,
    dust_pm10: float | None,
    rera_projects: list
) -> dict:
    """
    Combines visual classification, IoT environment data, and RERA approvals
    into an explainable Development Score and risk categorization.
    """
    base_score = progress if progress is not None else 0.0
    has_visual_construction = visual_stage not in (None, "", "Unknown") and base_score > 0.0
    if has_visual_construction:
        reasoning_steps = [f"Base score from construction progress: {base_score:.1f}%"]
    else:
        base_score = 0.0
        reasoning_steps = ["No verified construction progress because the uploaded image was classified as non-construction/irrelevant"]
    risk = "Medium"
    
    # 1. RERA Approval Scoring
    has_approval = False
    disputed = False
    
    if not has_visual_construction:
        if rera_projects:
            nearest_project = rera_projects[0]
            reasoning_steps.append(f"Nearby RERA record exists ({nearest_project.get('status')}) but the photo does not show a construction site")
        else:
            reasoning_steps.append("No registered RERA filing found within 500m")
    elif rera_projects:
        # Find nearest project status
        nearest_project = rera_projects[0]
        status = nearest_project.get("status", "").lower()
        if "approved" in status:
            has_approval = True
            base_score += 15.0
            reasoning_steps.append("Nearby verified RERA approval (+15 pts)")
        elif "disputed" in status or "unauthorized" in status:
            disputed = True
            base_score -= 30.0
            reasoning_steps.append("Unauthorized or Disputed site status detected (-30 pts)")
        else:
            reasoning_steps.append(f"Nearby project is pending RERA approval ({nearest_project.get('status')})")
    else:
        # No RERA match is a warning
        base_score -= 10.0
        reasoning_steps.append("No registered RERA filing found within 500m (-10 pts)")

    # 2. IoT Sensor Fusion (if active)
    mismatch = False
    environmental_hazard = False
    
    if sensor_status == "connected":
        has_noise = noise_db is not None
        has_pm25 = dust_pm25 is not None
        has_pm10 = dust_pm10 is not None

        # High noise & dust indicates heavy work
        if has_visual_construction and has_noise and has_pm25 and noise_db > 70.0 and dust_pm25 > 40.0:
            base_score += 10.0
            reasoning_steps.append("High noise and dust telemetry confirms active physical development (+10 pts)")
        
        # Mismatch check: Visual progress says active construction but sensors are completely silent
        if has_visual_construction and progress > 10.0 and progress < 90.0 and has_noise and noise_db < 50.0:
            mismatch = True
            base_score -= 15.0
            reasoning_steps.append("Mismatch: visual construction is in-progress but noise levels are extremely quiet (-15 pts)")
        if not has_visual_construction and ((has_noise and noise_db > 70.0) or (has_pm25 and dust_pm25 > 40.0)):
            reasoning_steps.append("Sensor activity is present, but visual analysis did not verify a construction site")
        
        # Environmental Hazard
        if (
            (has_noise and noise_db > 85.0)
            or (has_pm25 and dust_pm25 > 100.0)
            or (has_pm10 and dust_pm10 > 150.0)
        ):
            environmental_hazard = True
            reasoning_steps.append("Environmental warning: excessive noise or PM particulate levels measured at site")
        if not has_noise and not has_pm25 and not has_pm10:
            reasoning_steps.append("No dust/noise readings were supplied; environmental telemetry was not used")
    else:
        reasoning_steps.append("IoT sensor offline or un-correlated; scoring relies purely on visual and RERA records")

    # Limit score boundaries between 0 and 100
    final_score = max(0.0, min(100.0, base_score))

    # Risk Determination
    if not has_visual_construction:
        risk = "Low"
    elif disputed:
        risk = "High"
    elif mismatch or not rera_projects:
        risk = "Medium"
    else:
        risk = "Low"

    # Assemble summary
    summary_text = ". ".join(reasoning_steps)
    if mismatch:
        summary_text += ". [Warning: Activity mismatch - check for stalled worksite]."
    if environmental_hazard:
        summary_text += ". [Warning: High noise/dust environmental hazard]."

    return {
        "development_score": round(final_score, 1),
        "confidence": visual_confidence,
        "summary": summary_text,
        "risk": risk
    }
