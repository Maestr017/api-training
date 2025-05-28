from fastapi import HTTPException, Depends, APIRouter, status
from typing import List
from sqlalchemy.orm import Session
from pydantic import ValidationError
from src.models import Task
from src.schemas import TaskCreate, TaskEditStatus, TaskEditTitle, TaskResponse
from src.dependecies import get_db

main_router = APIRouter()

def validate_title_length(title: str):
    if len(title) < 1 or len(title) > 100:
        raise ValueError("Длина заголовка должна быть от 1 до 100 символов")
    return title

@main_router.post("/tasks/",
                 response_model=TaskResponse,
                 status_code=status.HTTP_201_CREATED,
                 responses={
                     400: {"description": "Некорректные данные задачи"},
                     500: {"description": "Ошибка сервера"}
                 })
async def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    try:
        validate_title_length(task.title)

        if db.query(Task).filter(Task.title == task.title).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Задача с таким названием уже существует"
            )

        db_task = Task(title=task.title, status_completed=task.status_completed)
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task

    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось создать задачу"
        )

@main_router.get("/tasks/",
                 response_model=List[TaskResponse],
                 responses={
                     500: {"description": "Ошибка сервера"}
                 })

async def get_tasks(db: Session = Depends(get_db)):
    try:
        return db.query(Task).all()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить список задач"
        )


@main_router.patch("/tasks/edit-status/{task_id}",
                   response_model=TaskResponse,
                   responses={
                       404: {"description": "Задача не найдена"},
                       400: {"description": "Некорректные данные"},
                       500: {"description": "Ошибка сервера"}
                   })
async def update_task_status(task_id: int, status_data: TaskEditStatus, db: Session = Depends(get_db)) -> TaskResponse:
    try:
        db_task = db.query(Task).filter(Task.id == task_id).first()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Задача с ID {task_id} не найдена"
            )

        if not isinstance(status_data.new_status, bool):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Статус должен быть boolean"
            )

        db_task.status_completed = status_data.new_status
        db.commit()
        db.refresh(db_task)

        return db_task

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить статус задачи"
        )

@main_router.patch("/tasks/edit-title/{task_id}",
                   response_model=TaskResponse,
                   responses={
                       404: {"description": "Задача не найдена"},
                       400: {"description": "Некорректное название"},
                       500: {"description": "Ошибка сервера"}
                   })
async def update_task_title(task_id: int, title_data: TaskEditTitle, db: Session = Depends(get_db)) -> TaskResponse:
    try:
        validate_title_length(title_data.new_title)
        db_task = db.query(Task).filter(Task.id == task_id).first()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Задача с ID {task_id} не найдена"
            )

        if db.query(Task).filter(Task.title == title_data.new_title, Task.id != task_id).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Задача с таким названием уже существует"
            )

        db_task.title = title_data.new_title
        db.commit()
        db.refresh(db_task)

        return db_task

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось обновить название задачи"
        )

@main_router.delete("/tasks/delete/{id}", response_model=TaskResponse)
async def delete_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    try:
        db_task = db.query(Task).filter(Task.id == task_id).first()

        if not db_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Задача с id {task_id} не найдена'
            )

        db.delete(db_task)
        db.commit()

        return db_task  # После коммита задача еще доступна
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось удалить задачу"
        )