from typing import List
from cloud.models import Observation

def build_prompt(question: str, nearby: List[Observation], history: List[Observation], latest: Observation) -> str:
    system_instructions = """You are the LandSense AI Construction Assistant.
Your primary role is to answer questions about the community construction data provided to you.
CRITICAL INSTRUCTIONS:
1. Use ONLY the supplied information below to answer the question.
2. If the answer cannot be found in the supplied information, or if no information is provided, you MUST reply exactly with: "There is currently no community information available."
3. NEVER hallucinate or use outside general knowledge."""

    nearby_text = "None"
    if nearby:
        nearby_text = "\n".join([f"- {o.summary} (Score: {o.development_score}, Dust: {o.dust_pm25}, Noise: {o.noise_db}, Stage: {o.construction_stage})" for o in nearby])
        
    history_text = "None"
    if history:
        history_text = "\n".join([f"- [{o.timestamp}] {o.summary} (Stage: {o.construction_stage}, Progress: {o.progress}%)" for o in history])
        
    latest_text = "None"
    if latest:
        latest_text = f"Dust: {latest.dust_pm25}, Noise: {latest.noise_db}, Stage: {latest.construction_stage} (Recorded at {latest.timestamp})"

    prompt = f"""{system_instructions}

---
SUPPLIED INFORMATION:

NEARBY OBSERVATIONS:
{nearby_text}

HISTORICAL OBSERVATIONS:
{history_text}

LATEST SENSOR READINGS:
{latest_text}

---
USER QUESTION: {question}

Answer:"""
    return prompt
