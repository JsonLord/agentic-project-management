import pytest
import respx
from httpx import Response
from app.services.dashboard import DashboardClient

@pytest.mark.asyncio
async def test_create_task():
    client = DashboardClient(base_url="https://mock-dashboard")

    async with respx.mock(base_url="https://mock-dashboard") as respx_mock:
        respx_mock.post("/api/tasks").mock(return_value=Response(200, json={"id": 1, "title": "Test Task", "status": "Planned", "type": "Code", "priority": "High", "assignee": None, "tags": [], "comments": 0}))

        response = await client.create_task("Test Task", "Code", "High")
        assert response["id"] == 1
        assert response["status"] == "Planned"

@pytest.mark.asyncio
async def test_get_state():
    client = DashboardClient(base_url="https://mock-dashboard")

    async with respx.mock(base_url="https://mock-dashboard") as respx_mock:
        respx_mock.get("/api/data").mock(return_value=Response(200, json={"tasks": []}))

        response = await client.get_state()
        assert "tasks" in response
