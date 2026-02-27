from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from app.services.dashboard import DashboardClient
from app.services.plandex import PlandexClient
from app.services.jules import JulesClient
from app.core.workflow import WorkflowManager, ProjectState

router = APIRouter()

class WebhookPayload(BaseModel):
    type: str  # "new_project", "update"
    description: Optional[str] = None
    project_name: Optional[str] = None
    repo_url: Optional[str] = None

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
    jules = JulesClient()

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

    session_id = await jules.create_session(f"Project: {project_name}")

    if tasks:
        first_task = tasks[0]
        await jules.submit_task(session_id, f"Implement: {first_task.get('title')}")

async def process_github_push(payload: GitHubPushPayload):
    dashboard = DashboardClient()
    repo_name = payload.repository.get("name", "unknown_repo")

    # Get current status
    current_status_str = await dashboard.get_project_status(repo_name)
    current_state = ProjectState(current_status_str.lower()) if current_status_str.lower() in [s.value for s in ProjectState] else ProjectState.PLANNED

    wf = WorkflowManager(current_state=current_state)

    # Analyze commits to update tasks
    for commit in payload.commits:
        msg = commit.message.lower()
        if "deploy" in msg:
            new_state = wf.next("deploy_success")
            await dashboard.log_activity(
                user_id=1,
                action=f"deployed ({new_state.value})",
                target=repo_name,
                time="now"
            )
        elif "test" in msg:
            new_state = wf.next("test_pass")
            await dashboard.log_activity(
                user_id=1,
                action=f"tested ({new_state.value})",
                target=repo_name,
                time="now"
            )
