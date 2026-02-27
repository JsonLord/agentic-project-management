import pytest
import respx
from httpx import Response
from app.services.jules import JulesClient

@pytest.mark.asyncio
async def test_create_session():
    client = JulesClient(base_url="https://mock-jules", profile="test_profile")

    async with respx.mock(base_url="https://mock-jules") as respx_mock:
        respx_mock.post("/api/sessions").mock(return_value=Response(200, json={"session_id": "sess_123"}))

        session_id = await client.create_session("New Project Context")
        assert session_id == "sess_123"
        # Verify headers
        assert respx_mock.calls.last.request.headers["X-Jules-Profile"] == "test_profile"

@pytest.mark.asyncio
async def test_submit_task():
    client = JulesClient(base_url="https://mock-jules", profile="test_profile")

    async with respx.mock(base_url="https://mock-jules") as respx_mock:
        respx_mock.post("/api/sessions/sess_123/tasks").mock(return_value=Response(200, json={"status": "queued"}))

        response = await client.submit_task("sess_123", "Write some code")
        assert response["status"] == "queued"
