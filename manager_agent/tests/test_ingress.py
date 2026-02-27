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
    coding_cli_url = settings.CODING_CLI_URL

    async with respx.mock(base_url=plandex_url) as plandex_mock, \
               respx.mock(base_url=dashboard_url) as dashboard_mock, \
               respx.mock(base_url=coding_cli_url) as coding_mock:

        # Setup Mocks
        plandex_mock.post("/api/plan").mock(return_value=Response(200, json={"tasks": [{"title": "Setup", "type": "Code"}]}))
        dashboard_mock.post("/api/tasks").mock(return_value=Response(200, json={"id": 1}))
        # Mocking upload-to-git
        coding_mock.post("/api/huggingface/upload-to-git").mock(return_value=Response(200, json={"status": "ok"}))

        # Create Payload
        payload = WebhookPayload(
            type="new_project",
            description="Build a rocket",
            project_name="RocketApp",
            space_id="rocket-space",
            repo_url="https://github.com/rocket/app"
        )

        # Run the logic directly
        await process_new_project(payload)

        # Assertions
        assert plandex_mock.calls.last.request.method == "POST"
        assert dashboard_mock.calls.last.request.method == "POST"

        # Verify Coding CLI call
        assert coding_mock.calls.last.request.method == "POST"
        assert b"rocket-space" in coding_mock.calls.last.request.content
