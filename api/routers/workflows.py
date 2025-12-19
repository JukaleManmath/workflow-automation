from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowRead
from db.session import get_session
from models.workflow import Workflow, WorkflowStep
from typing import List
from uuid import UUID

router = APIRouter()

# workflow creation router
@router.post("/workflow", status_code=status.HTTP_201_CREATED, response_model=WorkflowRead)
async def create_workflow(workflow: WorkflowCreate, db: Session = Depends(get_session)):
    new_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        trigger_type=workflow.trigger_type,
        cron_expression=workflow.cron_expression,
    )
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)

    for step in workflow.steps:
        db_step = WorkflowStep(
            workflow_id= new_workflow.id,
            name= step.name,
            type=step.type,
            position=step.position,
            config=step.config
        )
        db.add(db_step)
    db.commit()

    # reload the steps for response
    steps = db.exec(select(WorkflowStep).where(WorkflowStep.workflow_id == new_workflow.id)).all()
    new_workflow.steps = steps

    return new_workflow
    
    

# get all workflows
@router.get("/workflow", status_code=status.HTTP_200_OK, response_model=List[WorkflowRead])
async def get_all_workflow(db: Session = Depends(get_session)) -> dict:
    workflows = db.exec(select(Workflow)).all()
    # attach steps for each (simple mvp. approach)
    for wf in workflows:
        wf.steps = db.exec(select(WorkflowStep).where(WorkflowStep.workflow_id == wf.id)).all()
    return workflows


@router.get("/workflow/{workflow_id}", status_code=status.HTTP_200_OK, response_model=WorkflowRead)
async def get_workflow(workflow_id: UUID, db: Session = Depends(get_session)):

    workflow = db.exec(select(Workflow).where(Workflow.id == workflow_id)).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="workflow not found")
    
    workflow.steps = db.exec(select(WorkflowStep).where(WorkflowStep.workflow_id == workflow_id)).all()

    return workflow

@router.patch("/workflow/{workflow_id}", status_code=status.HTTP_200_OK, response_model=WorkflowRead)
async def upadte_workflow(workflow_id: UUID, payload: WorkflowUpdate, db: Session = Depends(get_session)):
    workflow = db.exec(select(Workflow).where(Workflow.id) == workflow_id).first()

    if not workflow:
        raise HTTPException(status_code=404, detail="workflow not found")
    
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(workflow, k, v)

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    workflow.steps = db.exec(select(WorkflowStep).where(WorkflowStep.workflow_id == workflow.id)).all()
    return workflow

