from fastapi import FastAPI
from sqlmodel import SQLModel
from db.session import engine
from api.routers.workflows import router as workflow_router
from api.routers.execution import router as run_router

app = FastAPI()

@app.on_event("startup")
def on_startup():
    # this will create all models imported in the application
    SQLModel.metadata.create_all(bind=engine)

app.include_router(router=workflow_router)
app.include_router(router=run_router)