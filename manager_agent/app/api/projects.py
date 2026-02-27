from fastapi import APIRouter, HTTPException, Depends
from app.services.dashboard import DashboardClient

router = APIRouter()

@router.get("/projects/{project_name}/status")
async def get_project_status(project_name: str):
    """
    Retrieve the current lifecycle status of a project.
    """
    dashboard = DashboardClient()
    status = await dashboard.get_project_status(project_name)
    return {"project": project_name, "status": status}
