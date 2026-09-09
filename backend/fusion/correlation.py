import math
from datetime import datetime, timezone
import logging

logger = logging.getLogger("landsense.correlation")

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth
    in meters using the Haversine formula.
    """
    if any(value is None for value in (lat1, lon1, lat2, lon2)):
        return float("inf")
    R = 6371000.0  # Radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c

def parse_iso_timestamp(ts_str: str | None) -> datetime | None:
    """
    Parses ISO 8601 string to offset-aware UTC datetime.
    Returns None for invalid/missing timestamps rather than inventing
    a current timestamp.
    """
    if not ts_str or not str(ts_str).strip():
        return None
    try:
        # Handle formats like "2026-07-08T09:40:00Z"
        ts = str(ts_str).strip()
        if ts.endswith("Z"):
            ts = ts[:-1] + "+00:00"
        parsed = datetime.fromisoformat(ts)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except Exception as exc:
        logger.warning("Error parsing timestamp %s: %s", ts_str, exc)
        return None

def correlate_sensor_data(
    phone_lat: float | None,
    phone_lon: float | None,
    phone_timestamp_str: str | None,
    sensor_data: dict,
    sensor_lat: float | None,
    sensor_lon: float | None,
) -> bool:
    """
    Applies the correlation rule:
    - Time difference between Phone and Arduino must be <= 30 seconds.
    - Distance between Phone and Arduino must be <= 50 meters.
    Missing/invalid coordinates or timestamps produce an explicit false
    and never a fabricated correlation result.
    """
    if not sensor_data:
        return False
    if phone_lat is None or phone_lon is None or sensor_lat is None or sensor_lon is None:
        logger.warning("Spatial correlation unavailable because a required GPS coordinate is missing or invalid.")
        return False
    try:
        phone_lat = float(phone_lat)
        phone_lon = float(phone_lon)
        sensor_lat = float(sensor_lat)
        sensor_lon = float(sensor_lon)
    except (TypeError, ValueError):
        logger.warning("Spatial correlation unavailable because a required GPS coordinate is non-numeric or invalid.")
        return False

    phone_ts = parse_iso_timestamp(phone_timestamp_str)
    sensor_ts = parse_iso_timestamp(sensor_data.get("timestamp", ""))
    if phone_ts is None or sensor_ts is None:
        logger.warning("Temporal correlation unavailable because one or both timestamps are missing or invalid.")
        return False

    time_diff = abs((phone_ts - sensor_ts).total_seconds())

    # 2. Calculate distance
    distance = haversine_distance(phone_lat, phone_lon, sensor_lat, sensor_lon)
    if distance == float("inf"):
        return False

    logger.info(f"Correlation check: Time Difference = {time_diff:.1f}s (Threshold: 30s), Distance = {distance:.1f}m (Threshold: 50m)")

    # 3. Apply validation thresholds
    if time_diff <= 30.0 and distance <= 50.0:
        return True

    return False
