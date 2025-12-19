from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy import Column, JSON


class WorkflowRun(SQLModel, table = True):

    __tablename__ = "workflow_runs"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    workflow_id: UUID = Field(foreign_key="workflows.id", index=True)

    input_payload: dict = Field(default_factory= dict , sa_column=Column(JSON))
    output: dict = Field(default_factory= dict , sa_column=Column(JSON))
    error_messages: dict = Field(default_factory= dict , sa_column=Column(JSON))

    status: str = Field(default="PENDING", index=True)

    run_started: datetime = Field(default_factory=datetime.utcnow)
    run_finished: Optional[datetime] = None

    step_runs: List["WorkflowStepRun"] = Relationship(back_populates="workflow_run")

class WorkflowStepRun(SQLModel, table=True):
    __tablename__ = "workflow_step_runs"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    workflow_step_id: UUID = Field(foreign_key="workflow_steps.id", index=True)
    workflow_run_id: UUID = Field(foreign_key="workflow_runs.id" , index=True)

    input_payload: dict = Field(default_factory= dict , sa_column=Column(JSON))
    output: dict = Field(default_factory= dict , sa_column=Column(JSON))
    error_messages: dict = Field(default_factory= dict , sa_column=Column(JSON))

    status: str = Field(default="PENDING", index=True)

    run_started: datetime = Field(default_factory=datetime.utcnow)
    run_finished: Optional[datetime] = None

    workflow_run: Optional[WorkflowRun] = Relationship(back_populates="step_runs")