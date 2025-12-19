from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy import Column, JSON

class Workflow(SQLModel, table = True):
    __tablename__ = "workflows"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)

    name: str
    description: Optional[str] = None

    trigger_type: str = Field(default=("MANUAL"))
    cron_expression: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Realationships
    steps: list["WorkflowStep"] = Relationship(back_populates="workflow")

class WorkflowStep(SQLModel, table=True):
    __tablename__ = "workflow_steps"

    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    workflow_id: UUID = Field(foreign_key="workflows.id", index=True)

    name: str
    type: str
    position: int

    config: dict = Field(default=dict, sa_column=Column(JSON))
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    workflow: Optional[Workflow] = Relationship(back_populates="steps")