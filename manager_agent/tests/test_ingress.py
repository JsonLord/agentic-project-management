import pytest
import respx
from httpx import Response
from app.api.webhooks import process_new_project, WebhookPayload
from app.core.config import settings

@pytest.mark.asyncio
async def test_process_new_project_flow():
    # Mock using the REAL URLs from settings
    plandex_url = settings.PLANDEX_URL
    dashboard_url = settings.DASHBOARD_URL
    jules_url = settings.JULES_API_URL

    async with respx.mock(base_url=plandex_url) as plandex_mock, \
               respx.mock(base_url=dashboard_url) as dashboard_mock, \
               respx.mock(base_url=jules_url) as jules_mock:

        # Setup Mocks
        plandex_mock.post("/api/plan").mock(return_value=Response(200, json={"tasks": [{"title": "Setup", "type": "Code"}]}))
        dashboard_mock.post("/api/tasks").mock(return_value=Response(200, json={"id": 1}))
        jules_mock.post("/api/sessions").mock(return_value=Response(200, json={"session_id": "sess_1"}))
        jules_mock.post("/api/sessions/sess_1/tasks").mock(return_value=Response(200, json={"status": "ok"}))

        # Create Payload
        payload = WebhookPayload(
            type="new_project",
            description="Build a rocket",
            project_name="RocketApp"
        )

        # Run the logic directly (bypass FastAPI routing to test orchestration)
        await process_new_project(payload)

        # Assertions
        assert plandex_mock.calls.last.request.method == "POST"
        assert dashboard_mock.calls.last.request.method == "POST"
        assert jules_mock.calls.call_count == 2 # Create session + Submit task
