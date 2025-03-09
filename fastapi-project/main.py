from fastapi import FastAPI
from pydantic import BaseModel
from uuid import UUID, uuid4
app = FastAPI()

class Tasks(BaseModel):
    id: UUID | None = None
    title: str
    description: str | None = None
    completed: bool = False
    
tasks = []

@app.post("/tasks/", response_model=list[Tasks])
def create_tasks(task: Tasks):
    new_task = task.model_copy(update={"id": uuid4()})
    tasks.append(new_task)
    return new_task

@app.get("/tasks/", response_model = list[Tasks])
def read_tasks():
    return tasks


#you can send curl request to test api
# curl -X POST http://127.0.0.1:8000/tasks/ \         
#      -H "Content-Type: application/json" \
#      -d '{"title": "OK it is working now yayayayayyayay", "description": "its workign bang bang bang", "completed": true}'


#can also do get reqest

# curl -X GET http://127.0.0.1:8000/tasks/