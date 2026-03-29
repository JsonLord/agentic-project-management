import pytest
import respx
from httpx import Response
from app.services.plandex import PlandexClient

@pytest.mark.asyncio
async def test_generate_plan():
    client = PlandexClient(base_url="https://mock-plandex")

    mock_plan = {
        "project_name": "Test Project",
        "tasks": [
            {"title": "Setup DB", "type": "backend"},
            {"title": "Create UI", "type": "frontend"}
        ]
    }

    async with respx.mock(base_url="https://mock-plandex") as respx_mock:
        respx_mock.post("/api/plan").mock(return_value=Response(200, json=mock_plan))

        response = await client.generate_plan("Build a todo app")
        assert response["project_name"] == "Test Project"
        assert len(response["tasks"]) == 2
