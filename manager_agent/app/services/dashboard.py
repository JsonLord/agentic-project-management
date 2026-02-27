import httpx
from typing import Dict, Any, List, Optional
from app.core.config import settings

class DashboardClient:
    def __init__(self, base_url: str = settings.DASHBOARD_URL):
        self.base_url = base_url

    async def get_state(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/data")
            response.raise_for_status()
            return response.json()

    async def get_project_status(self, project_name: str) -> str:
        """
        Helper to find the status of a project.
        Assumes there is a task representing the project or we derive it.
        For MVP: We look for a task with title 'Project: {project_name}'
        """
        try:
            state = await self.get_state()
            tasks = state.get("tasks", [])
            for task in tasks:
                if task.get("title") == f"Project: {project_name}":
                    return task.get("status", "Planned")
            return "Planned"
        except Exception:
            return "Planned"

    async def create_task(self, title: str, task_type: str, priority: str, status: str = "Planned", assignee: Optional[int] = None) -> Dict[str, Any]:
        payload = {
            "title": title,
            "type": task_type,
            "priority": priority,
            "status": status,
            "id": 0, # Placeholder
            "assignee": assignee,
            "tags": [],
            "comments": 0
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/tasks", json=payload)
            response.raise_for_status()
            return response.json()

    async def update_task(self, task_id: int, task_data: Dict[str, Any]) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.put(f"{self.base_url}/api/tasks/{task_id}", json=task_data)
            response.raise_for_status()
            return response.json()

    async def log_activity(self, user_id: int, action: str, target: str, time: str) -> Dict[str, Any]:
        payload = {
            "user": user_id,
            "action": action,
            "target": target,
            "time": time
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{self.base_url}/api/activities", json=payload)
            response.raise_for_status()
            return response.json()
