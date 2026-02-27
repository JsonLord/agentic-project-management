from httpx import AsyncClient
from app.core.config import settings
from typing import Dict, Any, List

class PlandexClient:
    def __init__(self, base_url: str = settings.PLANDEX_URL):
        self.base_url = base_url

    async def generate_plan(self, project_description: str) -> Dict[str, Any]:
        """
        Sends the project description to Plandex and receives a structured plan.
        """
        payload = {
            "description": project_description,
            "context": "new_project"
        }
        # Assuming Plandex has an endpoint /api/plan or similar based on prompt context implying "Plandex APIs"
        # Since we couldn't fetch docs, we'll design a robust client that can easily be pointed to the right path.
        # We'll assume POST /api/plan for now.
        async with AsyncClient() as client:
            # We'll set a timeout as planning might take time
            response = await client.post(f"{self.base_url}/api/plan", json=payload, timeout=60.0)
            # If the endpoint is different, we'd update it here.
            # For now, we handle potential 404s or errors gracefully in the Orchestrator,
            # but here we raise to signal failure.
            response.raise_for_status()
            return response.json()
