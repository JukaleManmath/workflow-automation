from sqlmodel import SQLModel, create_engine, Session
from core.config import settings

# Creating a db engine
engine = create_engine(settings.DATABASE_URL, echo =True)


# dependency to get a DB session in routes
def get_session():
    with Session(engine) as session:
        yield session
