import pytest
import respx
from httpx import Response
from app.api.webhooks import process_github_push, GitHubPushPayload, GitHubCommit
from app.core.config import settings

@pytest.mark.asyncio
async def test_process_github_push():
    dashboard_url = settings.DASHBOARD_URL

    async with respx.mock(base_url=dashboard_url) as dashboard_mock:
        # Mock GET /api/data
        dashboard_mock.get("/api/data").mock(return_value=Response(200, json={
            "tasks": [{"id": 100, "title": "Project: RocketApp", "status": "Adapted", "type": "Project", "priority": "High"}]
        }))

        # Mock update task
        dashboard_mock.put("/api/tasks/100").mock(return_value=Response(200, json={"id": 100, "status": "Deployed"}))

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
        # 1. Fetched State
        assert dashboard_mock.calls.contains(lambda r: r.method == "GET" and r.url.path == "/api/data")

        # 2. Updated Task (Adapted -> Deployed)
        assert dashboard_mock.calls.contains(lambda r: r.method == "PUT" and r.url.path == "/api/tasks/100")

        # 3. Logged Activity
        assert dashboard_mock.calls.last.request.method == "POST"
        assert b"status_change (deployed)" in dashboard_mock.calls.last.request.content
