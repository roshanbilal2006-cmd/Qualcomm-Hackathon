import logging

logger = logging.getLogger("landsense.scoring")

def calculate_development_score(
    visual_stage: str,
    progress: float,
    visual_confidence: float,
    sensor_status: str,
    noise_db: float,
    dust_pm25: float,
    dust_pm10: float,
    rera_projects: list
) -> dict:
    """
    Combines visual classification, IoT environment data, and RERA approvals
    into an explainable Development Score and risk categorization.
    """
    base_score = progress if progress is not None else 0.0
    reasoning_steps = [f"Base score from construction progress: {base_score:.1f}%"]
    risk = "Medium"
    
    # 1. RERA Approval Scoring
    has_approval = False
    disputed = False
    
    if rera_projects:
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
        # High noise & dust indicates heavy work
        if noise_db > 70.0 and dust_pm25 > 40.0:
            base_score += 10.0
            reasoning_steps.append("High noise and dust telemetry confirms active physical development (+10 pts)")
        
        # Mismatch check: Visual progress says active construction but sensors are completely silent
        if progress > 10.0 and progress < 90.0 and noise_db < 50.0:
            mismatch = True
            base_score -= 15.0
            reasoning_steps.append("Mismatch: visual construction is in-progress but noise levels are extremely quiet (-15 pts)")
        
        # Environmental Hazard
        if noise_db > 85.0 or dust_pm25 > 100.0 or dust_pm10 > 150.0:
            environmental_hazard = True
            reasoning_steps.append("Environmental warning: excessive noise or PM particulate levels measured at site")
    else:
        reasoning_steps.append("IoT sensor offline or un-correlated; scoring relies purely on visual and RERA records")

    # Limit score boundaries between 0 and 100
    final_score = max(0.0, min(100.0, base_score))

    # Risk Determination
    if disputed:
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
