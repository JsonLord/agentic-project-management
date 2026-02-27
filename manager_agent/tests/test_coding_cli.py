import pytest
import respx
from httpx import Response
from app.services.coding_cli import CodingCLIClient

@pytest.mark.asyncio
async def test_get_branches():
    client = CodingCLIClient(base_url="https://mock-cli", profile="test_profile")

    async with respx.mock(base_url="https://mock-cli") as respx_mock:
        respx_mock.get("/api/github/branches").mock(return_value=Response(200, json={"branches": ["main", "feature/1"]}))

        branches = await client.get_branches("https://github.com/owner/repo")
        assert "main" in branches
        assert len(branches) == 2

@pytest.mark.asyncio
async def test_merge_repos():
    client = CodingCLIClient(base_url="https://mock-cli", profile="test_profile")

    async with respx.mock(base_url="https://mock-cli") as respx_mock:
        respx_mock.post("/api/github/merge").mock(return_value=Response(200, json={"status": "merged"}))

        response = await client.merge_repos("src_repo", "tgt_repo")
        assert response["status"] == "merged"

@pytest.mark.asyncio
async def test_upload_to_git():
    client = CodingCLIClient(base_url="https://mock-cli", profile="test_profile")

    async with respx.mock(base_url="https://mock-cli") as respx_mock:
        respx_mock.post("/api/huggingface/upload-to-git").mock(return_value=Response(200, json={"commit_sha": "abc1234"}))

        response = await client.upload_to_git("my-space", "https://github.com/owner/repo")
        assert response["commit_sha"] == "abc1234"
