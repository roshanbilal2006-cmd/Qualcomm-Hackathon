import httpx
import logging

logger = logging.getLogger("landsense.mcp_adapter")

class MCPAdapter:
    def __init__(self, service_url: str = "http://localhost:8004"):
        self.service_url = service_url

    async def get_nearby_projects(self, latitude: float, longitude: float, radius_meters: float = 500.0) -> list:
        """
        Retrieves nearby RERA projects and status via the MCP adapter.
        """
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(
                    f"{self.service_url}/nearby_projects",
                    params={"latitude": latitude, "longitude": longitude, "radius_meters": radius_meters}
                )
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"MCP Service returned status code {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to connect to MCP Service at {self.service_url}: {str(e)}")

        return []
