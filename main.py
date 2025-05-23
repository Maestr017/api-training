from fastapi import FastAPI, HTTPException
from typing import Optional, List, Dict
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    id: int
    title: str
    status_completed: bool

tasks = [
    {'id': 1, 'title': 'text 1', 'status_completed': False},
    {'id': 2, 'title': 'text 2', 'status_completed': False},
    {'id': 3, 'title': 'text 3', 'status_completed': False}
]


@app.get("/items")
async def items() -> List[Task]:
    return [Task(**task) for task in tasks]

@app.get("/items/{id}")
async def items(id: int) -> Task:
    for task in tasks:
        if task['id'] == id:
            return Task(**task)

    raise HTTPException(status_code=404, detail='Task not found')

@app.get("/search")
async def search(task_id: Optional[int] = None) -> Dict[str, Optional[Task]]:
    if task_id:
        for task in tasks:
            if task['id'] == task_id:
                return {"data": Task(**task)}

        raise HTTPException(status_code=404, detail='Task not found')
    else:
        return {"data": None}
