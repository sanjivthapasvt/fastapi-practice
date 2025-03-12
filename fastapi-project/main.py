from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import Optional, Annotated, Union
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import Depends, FastAPI, HTTPException, Query

class TasksBase(SQLModel):
    title: str = Field(index=True)
    description: str = Field
    completed: bool = Field(default=False)

class Tasks(TasksBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class TasksPublic(TasksBase):
    id: int
    
class TasksCreate(TasksBase):
    pass

class TasksUpdate(TasksBase):
    title: str | None
    description: str | None
    completed: bool | None

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
async def on_startup():
    create_db_and_tables()

@app.post("/tasks/", response_model=TasksPublic)
async def create_tasks(task: TasksCreate, session: SessionDep) -> Tasks:
    db_task = Tasks.model_validate(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

@app.get("/tasks/", response_model=list[TasksPublic])
async def read_tasks(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100) -> list[Tasks]:
    tasks = session.exec(select(Tasks).offset(offset).limit(limit)).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TasksPublic)
async def read_task(task_id: int, session: SessionDep) -> Tasks:
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.patch("/tasks/{task_id}", response_model=TasksPublic)
async def update_task(task_id: int, task: TasksUpdate, session: SessionDep) -> Tasks:
    task_db = session.get(Tasks, task_id)
    if not task_db:
        raise HTTPException(status_code=404, detail="Item not found")
   
    task_data = task.model_dump(exclude_unset=True)
    task_db.sqlmodel_update(task_data)
    session.add(task_db)
    session.commit()
    session.refresh(task_db)
    return task_db

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, session: SessionDep):
    task = session.get(Tasks, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}
