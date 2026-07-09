# utils/request_id.py
"""
Request ID generation for correlating logs across a single request.
"""

import uuid


def generate_request_id() -> str:
    return uuid.uuid4().hex[:12]