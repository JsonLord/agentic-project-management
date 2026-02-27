from httpx import AsyncClient
from app.core.config import settings
from typing import Dict, Any, List, Optional

class CodingCLIClient:
    def __init__(self, base_url: str = settings.CODING_CLI_URL, profile: str = settings.JULES_PROFILE):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {profile}",
            "X-Jules-Profile": profile
        }

    async def get_branches(self, repo_url: str) -> List[str]:
        """
        Discover branches for a given repo.
        """
        params = {"repo_url": repo_url}
        async with AsyncClient(headers=self.headers) as client:
            response = await client.get(f"{self.base_url}/api/github/branches", params=params)
            response.raise_for_status()
            return response.json().get("branches", [])

    async def merge_repos(self, source_repo: str, target_repo: str, branch: str = "main") -> Dict[str, Any]:
        """
        Merge code from source repo to target repo.
        """
        payload = {
            "source_repo": source_repo,
            "target_repo": target_repo,
            "branch": branch
        }
        async with AsyncClient(headers=self.headers) as client:
            response = await client.post(f"{self.base_url}/api/github/merge", json=payload)
            response.raise_for_status()
            return response.json()

    async def upload_to_git(self, space_id: str, repo_url: str, message: str = "Sync from space") -> Dict[str, Any]:
        """
        Sync a Hugging Face Space to a GitHub repository.
        """
        payload = {
            "space_id": space_id,
            "repo_url": repo_url,
            "commit_message": message
        }
        async with AsyncClient(headers=self.headers) as client:
            response = await client.post(f"{self.base_url}/api/huggingface/upload-to-git", json=payload)
            response.raise_for_status()
            return response.json()
