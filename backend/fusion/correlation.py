import math
from datetime import datetime, timezone
import logging

logger = logging.getLogger("landsense.correlation")

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth
    in meters using the Haversine formula.
    """
    R = 6371000.0  # Radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return R * c

def parse_iso_timestamp(ts_str: str) -> datetime:
    """
    Parses ISO 8601 string to offset-aware UTC datetime.
    """
    try:
        # Handle formats like "2026-07-08T09:40:00Z"
        if ts_str.endswith("Z"):
            ts_str = ts_str[:-1] + "+00:00"
        return datetime.fromisoformat(ts_str)
    except Exception as e:
        logger.error(f"Error parsing timestamp {ts_str}: {str(e)}")
        return datetime.now(timezone.utc)

def correlate_sensor_data(
    phone_lat: float,
    phone_lon: float,
    phone_timestamp_str: str,
    sensor_data: dict,
    sensor_lat: float,
    sensor_lon: float
) -> bool:
    """
    Applies the correlation rule:
    - Time difference between Phone and Arduino must be <= 30 seconds.
    - Distance between Phone and Arduino must be <= 50 meters.
    """
    if not sensor_data:
        return False

    # 1. Parse timestamps
    phone_ts = parse_iso_timestamp(phone_timestamp_str)
    sensor_ts = parse_iso_timestamp(sensor_data.get("timestamp", ""))

    time_diff = abs((phone_ts - sensor_ts).total_seconds())

    # 2. Calculate distance
    distance = haversine_distance(phone_lat, phone_lon, sensor_lat, sensor_lon)

    logger.info(f"Correlation check: Time Difference = {time_diff:.1f}s (Threshold: 30s), Distance = {distance:.1f}m (Threshold: 50m)")

    # 3. Apply validation thresholds
    if time_diff <= 30.0 and distance <= 50.0:
        return True

    return False
