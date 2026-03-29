import pytest
import respx
from httpx import Response, AsyncClient
from app.main import app
from app.core.config import settings

@pytest.mark.asyncio
async def test_get_project_status():
    dashboard_url = settings.DASHBOARD_URL

    async with respx.mock(base_url=dashboard_url) as dashboard_mock:
        dashboard_mock.get("/api/data").mock(return_value=Response(200, json={
            "tasks": [{"title": "Project: RocketApp", "status": "Deployed"}]
        }))

        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/projects/RocketApp/status")
            assert response.status_code == 200
            assert response.json()["status"] == "Deployed"
