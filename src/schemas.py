from pydantic import BaseModel, Field

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description='Размер задачи от 1 до 100 символов')
    status_completed: bool = Field(False)

class TaskResponse(TaskBase):
    id: int = Field(..., title='Здесь указыватеся id задания', ge=1)

    class Config:
        orm_mode = True


class TaskEditTitle(TaskBase):
    new_title: str = Field(..., min_length=1, max_length=100, description='Размер задачи от 1 до 100 символов')

class TaskEditStatus(TaskBase):
    new_status: bool

class TaskCreate(TaskBase):
    pass