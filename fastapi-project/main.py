from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import Optional, Annotated, Union
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import Depends, FastAPI, HTTPException, Query

class Tasks(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str = Field()
    completed: bool = Field(default=False)
    

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/tasks/")
def create_tasks(task: Tasks, session: SessionDep) -> Tasks:
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/tasks/")
def read_tasks(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100) -> list[Tasks]:
    tasks = session.exec(select(Tasks).offset(offset).limit(limit)).all()
    return tasks

@app.get("/tasks/{task_id}")
def read_task(task_id: int, session: SessionDep) -> Tasks:
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task
@app.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Tasks, session: SessionDep) -> Tasks:
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Item not found")
    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: SessionDep) -> Tasks:
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}
