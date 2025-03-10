from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import UUID, uuid4
from typing import Optional

app = FastAPI()

class Tasks(BaseModel):
    id: Optional[UUID] = None
    title: str
    description: str | None = None
    completed: bool = False
    
tasks = []

@app.post("/tasks/", response_model=Tasks)
def create_tasks(task: Tasks):
    new_task = task.model_copy(update={"id": uuid4()})
    tasks.append(new_task)
    return new_task.model_dump()

@app.get("/tasks/", response_model = list[Tasks])
def read_tasks():
    return tasks

@app.get("/tasks/{task_id}", response_model=Tasks)
def read_task(task_id: UUID):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}", response_model=Tasks)
def update_task(task_id: UUID, task_update: Tasks):
    for index, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = task.copy(update=task_update.model_dump(exclude_unset=True))
            tasks[index] = updated_task
            return updated_task
    raise HTTPException(status_code=404, detail="Item not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: UUID):
    for task in tasks:
        if task.id == task_id:
            tasks.remove(task)
            return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")
