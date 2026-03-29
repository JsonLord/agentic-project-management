from enum import Enum
from typing import Optional

class ProjectState(str, Enum):
    PLANNED = "planned"
    ADAPTED = "adapted"
    DEPLOYED = "deployed"
    RUNNING = "running"
    TESTED = "tested"

class WorkflowManager:
    """
    Manages the lifecycle of a project component.
    """
    def __init__(self, current_state: ProjectState = ProjectState.PLANNED):
        self.state = current_state

    def next(self, event: str) -> ProjectState:
        """
        Transition state based on event.
        Events: 'adaptation_complete', 'deploy_success', 'startup_success', 'test_pass'
        """
        if self.state == ProjectState.PLANNED and event == "adaptation_complete":
            self.state = ProjectState.ADAPTED
        elif self.state == ProjectState.ADAPTED and event == "deploy_success":
            self.state = ProjectState.DEPLOYED
        elif self.state == ProjectState.DEPLOYED and event == "startup_success":
            self.state = ProjectState.RUNNING
        elif self.state == ProjectState.RUNNING and event == "test_pass":
            self.state = ProjectState.TESTED
        return self.state
