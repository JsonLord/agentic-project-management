from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.dashboard import DashboardClient
from app.services.plandex import PlandexClient
from app.services.coding_cli import CodingCLIClient
from app.core.workflow import WorkflowManager, ProjectState

router = APIRouter()

class WebhookPayload(BaseModel):
    type: str  # "new_project", "update"
    description: Optional[str] = None
    project_name: Optional[str] = None
    repo_url: Optional[str] = None
    space_id: Optional[str] = None

class GitHubCommit(BaseModel):
    id: str
    message: str
    url: str

class GitHubPushPayload(BaseModel):
    ref: str
    commits: List[GitHubCommit]
    repository: Dict[str, Any]

@router.post("/webhook/ingress")
async def handle_webhook(payload: WebhookPayload, background_tasks: BackgroundTasks):
    """
    Ingress point for new projects or updates.
    """
    if payload.type == "new_project":
        background_tasks.add_task(process_new_project, payload)
        return {"status": "processing", "message": "Project planning started"}

    return {"status": "ignored", "message": "Unknown type"}

@router.post("/webhook/github")
async def handle_github_webhook(payload: GitHubPushPayload, background_tasks: BackgroundTasks):
    """
    Ingress point for GitHub webhooks.
    """
    background_tasks.add_task(process_github_push, payload)
    return {"status": "processing", "message": "GitHub push received"}

async def process_new_project(payload: WebhookPayload):
    dashboard = DashboardClient()
    plandex = PlandexClient()
    coding_cli = CodingCLIClient()

    try:
        plan = await plandex.generate_plan(payload.description or "No Description")
    except Exception as e:
        print(f"Error generating plan: {e}")
        return

    # Create Project Task to track status
    project_name = payload.project_name or "New Project"
    await dashboard.create_task(
        title=f"Project: {project_name}",
        task_type="Project",
        priority="High",
        status="Planned"
    )

    tasks = plan.get("tasks", [])
    for task in tasks:
        await dashboard.create_task(
            title=task.get("title", "Untitled Task"),
            task_type=task.get("type", "Code"),
            priority=task.get("priority", "Medium"),
            status="Planned"
        )

    if payload.space_id and payload.repo_url:
        try:
            await coding_cli.upload_to_git(
                space_id=payload.space_id,
                repo_url=payload.repo_url,
                message=f"Initialize project: {project_name}"
            )
        except Exception as e:
            print(f"Error syncing to git: {e}")

async def process_github_push(payload: GitHubPushPayload):
    dashboard = DashboardClient()
    repo_name = payload.repository.get("name", "unknown_repo")

    # Get current status
    project_task = await dashboard.get_project_task(repo_name)
    current_status_str = project_task.get("status", "Planned") if project_task else "Planned"
    task_id = project_task.get("id") if project_task else None

    current_state = ProjectState(current_status_str.lower()) if current_status_str.lower() in [s.value for s in ProjectState] else ProjectState.PLANNED

    wf = WorkflowManager(current_state=current_state)

    # Analyze commits to update tasks
    new_state = None
    for commit in payload.commits:
        msg = commit.message.lower()
        if "deploy" in msg:
            new_state = wf.next("deploy_success")
        elif "test" in msg:
            new_state = wf.next("test_pass")

    if new_state:
        # Update Dashboard State
        if task_id:
            # We need to preserve other fields? The DashboardClient.update_task updates what we send?
            # Ideally we fetch the whole task and update status, or backend supports partial.
            # Assuming partial update or we just send what we know.
            # To be safe, we might just send the status update if API supports it,
            # or merge with what we got from get_project_task.
            updated_data = project_task.copy() if project_task else {}
            updated_data["status"] = new_state.value.capitalize()
            await dashboard.update_task(task_id, updated_data)

        # Log Activity
        await dashboard.log_activity(
            user_id=1,
            action=f"status_change ({new_state.value})",
            target=repo_name,
            time="now"
        )
