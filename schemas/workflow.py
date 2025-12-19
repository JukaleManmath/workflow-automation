from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


# Workflow step schemas
class WorkflowStepBase(BaseModel):
    name: str
    type: str
    position: int
    config: dict = Field(default_factory=dict)

class WorkflowStepCreate(WorkflowStepBase):
    pass

class WorkflowStepRead(WorkflowStepBase):
    id: UUID
    workflow_id: UUID


# Workflow schemas

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: Optional[str] = "MANUAL"
    cron_expression:Optional[str] = None


# for api -> creating a workflow
class WorkflowCreate(WorkflowBase):
    steps: List[WorkflowStepCreate] = Field(default_factory=list)

# for updating a workflow
class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_type: Optional[str] = None
    cron_expression: Optional[str] = None

# for api: Reading a workflow (response)
class WorkflowRead(WorkflowBase):
    id: UUID
    steps: List[WorkflowStepRead] = Field(default_factory=list)

# execution request/response schemas
class WorkflowRunRequest(BaseModel):
    input: dict = Field(default_factory=dict)

class WorkflowRunResponse(BaseModel):
    workflow_run_id: UUID
    status: str
    output: dict = Field(default_factory=dict)
    error_messages: dict = Field(default_factory=dict)
