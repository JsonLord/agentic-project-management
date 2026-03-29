import pytest
from app.core.workflow import WorkflowManager, ProjectState

def test_workflow_transitions():
    wf = WorkflowManager()
    assert wf.state == ProjectState.PLANNED

    wf.next("adaptation_complete")
    assert wf.state == ProjectState.ADAPTED

    wf.next("deploy_success")
    assert wf.state == ProjectState.DEPLOYED

    wf.next("startup_success")
    assert wf.state == ProjectState.RUNNING

    wf.next("test_pass")
    assert wf.state == ProjectState.TESTED

def test_invalid_transition():
    wf = WorkflowManager()
    wf.next("deploy_success") # Should not skip steps
    assert wf.state == ProjectState.PLANNED
