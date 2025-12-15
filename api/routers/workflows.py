from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowRead
from db.session import get_session
from models.workflow import Workflow, WorkflowStep
from typing import List

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
    db.refresh(new_workflow)

    return new_workflow
    
    

# get all workflows
@router.get("/workflow", status_code=status.HTTP_200_OK, response_model=List[WorkflowRead])
async def get_all_workflow(db: Session = Depends(get_session)) -> dict:
    workflows = db.exec(select(Workflow)).all()
    return workflows