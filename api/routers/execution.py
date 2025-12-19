from fastapi import APIRouter, Depends, HTTPException, status
from db.session import get_session
from sqlmodel import Session, select
from services.workflow_executor import execute_workflow
from uuid import UUID
from schemas.workflow import WorkflowRunRequest, WorkflowRunResponse
from models.workflow_run import WorkflowRun, WorkflowStepRun
from typing import List


router = APIRouter()

#workflow run route
@router.post("/workflow/{workflow_id}/run", status_code=status.HTTP_200_OK, response_model=WorkflowRunResponse)
async def run_workflow(workflow_id: UUID, body: WorkflowRunRequest, db: Session = Depends(get_session)):

    run = await execute_workflow(workflow_id, db, body.input)
    return WorkflowRunResponse(
        workflow_run_id = run.id,
        status= run.status,
        output=run.output,
        error_messages=run.error_messages
    )

@router.get("/workflows/{workflow_id}/runs", status_code=status.HTTP_200_OK, response_model= List[WorkflowRun])
async def get_workflow_runs(workflow_id: UUID, db: Session = Depends(get_session)):
    runs = db.exec(select(WorkflowRun).where(WorkflowRun.workflow_id == workflow_id)).all()
    return runs

@router.get("/runs/{run_id}/steps", status_code=status.HTTP_200_OK, response_model=List[WorkflowStepRun])
async def list_step_runs(run_id: UUID, db: Session = Depends(get_session)):
    steps = db.exec(select(WorkflowStepRun).where(WorkflowStepRun.workflow_run_id == run_id)).all()
    return steps