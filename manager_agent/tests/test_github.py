import pytest
import respx
from httpx import Response
from app.api.webhooks import process_github_push, GitHubPushPayload, GitHubCommit
from app.core.config import settings

@pytest.mark.asyncio
async def test_process_github_push():
    dashboard_url = settings.DASHBOARD_URL

    async with respx.mock(base_url=dashboard_url) as dashboard_mock:
        # Mock GET /api/data for get_project_status
        dashboard_mock.get("/api/data").mock(return_value=Response(200, json={
            "tasks": [{"title": "Project: RocketApp", "status": "Adapted"}]
        }))

        # Mock log activity
        dashboard_mock.post("/api/activities").mock(return_value=Response(200, json={"status": "ok"}))

        payload = GitHubPushPayload(
            ref="refs/heads/main",
            commits=[
                GitHubCommit(id="abc", message="deploy: Initial release", url="http://github.com/repo/commit/abc")
            ],
            repository={"name": "RocketApp"}
        )

        await process_github_push(payload)

        # Verification
        # 1. It should have fetched state
        assert dashboard_mock.calls.contains(lambda r: r.method == "GET" and r.url.path == "/api/data")

        # 2. It should have logged activity "deployed (deployed)" because Adapted -> deploy_success -> Deployed
        assert dashboard_mock.calls.last.request.method == "POST"
        assert b"deployed (deployed)" in dashboard_mock.calls.last.request.content
