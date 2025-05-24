from fastapi import FastAPI, HTTPException
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

app = FastAPI()

class TaskEditTitle(BaseModel):
    id: int
    new_title: str = Field(..., min_length=1, max_length=100, description='Новый размер задачи от 1 до 100 символов')
    status: bool

class TaskEditStatus(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=100, description='Размер задачи от 1 до 100 символов')
    new_status: bool

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description='Размер задачи от 1 до 100 символов')
    status_completed: bool

class Task(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=100, description='Размер задачи от 1 до 100 символов')
    status_completed: bool

tasks = [
    {'id': 0, 'title': 'text 1', 'status_completed': False},
    {'id': 1, 'title': 'text 2', 'status_completed': False},
    {'id': 2, 'title': 'text 3', 'status_completed': False}
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


@app.post("/items/add")
async def add_items(task: TaskCreate) -> Task:
    new_task_id = len(tasks) + 1
    new_task = {'id': new_task_id, 'title': task.title, 'status_completed':task.status_completed}
    tasks.append(new_task)

    return Task(**new_task)

@app.put("/items/edit-status/{id}")
async def edit_status(id: int, task_data: TaskEditStatus) -> Task:
    if id != task_data.id:
        raise HTTPException(status_code=400, detail="ID в пути и теле запроса не совпадают")

    task_to_update = None
    for task in tasks:
        if task['id'] == id:
            task_to_update = task
            break

    if not task_to_update:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task_to_update['status_completed'] = task_data.new_status

    return Task(**task_to_update)

@app.put("/items/edit-title/{id}")
async def edit_title(id: int, task_data: TaskEditTitle) -> Task:
    if id != task_data.id:
        raise HTTPException(status_code=400, detail="ID в пути и теле запроса не совпадают")

    task_to_update = None
    for task in tasks:
        if task['id'] == id:
            task_to_update = task
            break

    if not task_to_update:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    task_to_update['title'] = task_data.new_title

    return Task(**task_to_update)

@app.delete("/items/delete-task/{id}")
async def delete_task(id: int) -> Dict:
    task_to_delete = None
    for i, task in enumerate(tasks):
        if task['id'] == id:
            task_to_delete = tasks.pop(i)
            break

    if not task_to_delete:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return {
        "status": 'успех',
        "message": f'Задача с ID {id} удалена',
        "deleted_task": task_to_delete
    }