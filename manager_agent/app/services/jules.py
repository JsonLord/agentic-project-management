from httpx import AsyncClient
from app.core.config import settings
from typing import Dict, Any, Optional

class JulesClient:
    def __init__(self, base_url: str = settings.JULES_API_URL, profile: str = settings.JULES_PROFILE):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {profile}",
            "X-Jules-Profile": profile
        }

    async def create_session(self, context: str) -> str:
        """
        Creates a new coding session.
        Returns: session_id
        """
        payload = {"context": context}
        async with AsyncClient(headers=self.headers) as client:
            response = await client.post(f"{self.base_url}/api/sessions", json=payload)
            response.raise_for_status()
            return response.json().get("session_id")

    async def submit_task(self, session_id: str, description: str, files: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Submits a task to an active session.
        """
        payload = {
            "session_id": session_id,
            "instruction": description,
            "files": files or {}
        }
        async with AsyncClient(headers=self.headers) as client:
            # Assuming a task execution endpoint
            response = await client.post(f"{self.base_url}/api/sessions/{session_id}/tasks", json=payload)
            response.raise_for_status()
            return response.json()
