
from fastapi import HTTPException
from typing import Dict, Any
from datetime import datetime

from models.workflow import Workflow, WorkflowStep
from sqlmodel import select
from services.step_handlers import HANDLER_REGISTRY
from models.workflow_run import WorkflowRun, WorkflowStepRun



def _validate_steps(steps: list[WorkflowStep]) -> None:
    if not steps:
        raise HTTPException(status_code=400, detail="workflow has no steps")

    positions = [s.position for s in steps]
    if any(p is None for p in positions):
        raise HTTPException(status_code=400, detail="All steps must have position")

    if len(set(positions)) < len(positions):
        raise HTTPException(status_code=400, detail="step positions must be unique")



async def execute_workflow(workflow_id, db, input_payload: dict):
    # load the workflow
    workflow = db.exec(select(Workflow).where(Workflow.id == workflow_id)).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # load the steps explicitly (more reliable than workflow.steps)
    steps = db.exec(select(WorkflowStep).where(WorkflowStep.workflow_id == workflow_id)).all()
    _validate_steps(steps)

    steps.sort(key = lambda s: s.position)

    #create a workflow run
    context : Dict[str, Any] = {"input": input_payload}

    workflow_run = WorkflowRun(
        workflow_id=workflow.id,
        input_payload=input_payload,
        status="RUNNING",
        run_started= datetime.utcnow()
    )

    db.add(workflow_run)
    db.commit()
    db.refresh(workflow_run)

    # execute steps with pre-step persistence
    try:
        for step in steps:
            handler = HANDLER_REGISTRY.get(step.type)
            if not handler:
                # if handler not found record the step run as failed
                step_run = WorkflowStepRun(
                    workflow_step_id=step.id,
                    workflow_run_id=workflow_run.id,
                    input_payload={"config": step.config, "context_keys": list(context.keys())},
                    status="FAILED",
                    error_messages={"error": f"No handler registered for this step type: {step.type}"},
                    run_started= datetime.utcnow(),
                    run_finished= datetime.utcnow(),
                )

                db.add(step_run)
                
                workflow_run.status = "FAILED"
                workflow_run.error_messages = {"error": f"No handler registered for this step type: {step.type}"}
                workflow_run.run_finished = datetime.utcnow()
                db.add(workflow_run)
                db.commit()
                raise HTTPException(status_code=400, detail = f"No handler for step type: {step.type}")
            
            # create a step run
            step_run = WorkflowStepRun(
                workflow_step_id=step.id,
                workflow_run_id=workflow_run.id,
                input_payload={"config": step.config},
                status="RUNNING",
                run_started= datetime.utcnow()
            )
            db.add(step_run)
            db.commit()
            db.refresh(step_run)


            result = await handler.run(step, context)
            status_str = result.get("status", "FAILED")

            patch = result.get("context_patch", "")
            if patch:
                context.update(patch)
                
            # fianlize the final step_run
            step_run.output = result.get("output") or {}
            step_run.error_messages = {"error": result.get("error")} if result.get("error") else {}
            step_run.status = "SUCCESS" if status_str == "SUCCESS" else "FAILED"
            step_run.run_finished = datetime.utcnow()
            db.add(step_run)
            db.commit()
            db.refresh(step_run)

            if step_run.status == "FAILED":
                db.rollback()
                workflow_run.status = "FAILED"
                workflow_run.error_messages = {
                    "failed_step_id": str(step.id),
                    "failed_step_name": step.name,
                    "error": step_run.error_messages,
                }

                workflow_run.output = {"context": context}
                workflow_run.run_finished = datetime.utcnow()
                db.add(workflow_run)
                db.commit()
                db.refresh(workflow_run)

                return workflow_run

            # success finalize run
        workflow_run.status = "SUCCESS"
        workflow_run.output = {"context": context}
        workflow_run.run_finished = datetime.utcnow()
        db.add(workflow_run)
        db.commit()
        db.refresh(workflow_run)

        return workflow_run
    
    except Exception as e:
        db.rollback()
        workflow_run.status = "FAILED"
        workflow_run.error_messages = {"error": str(e)}
        workflow_run.output = {"context": context}
        workflow_run.run_finished = datetime.utcnow()
        db.add(workflow_run)
        db.commit()
        db.refresh(workflow_run)
        raise HTTPException(status_code=500, detail=str(e))


