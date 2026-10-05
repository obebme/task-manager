from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

from services.task_service import TaskService
from utils.storage import load_tasks, save_tasks


app = FastAPI(
    title="Task Manager API",
    version="1.0.0"
)

service = TaskService(load_tasks())


class TaskCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    completed: bool | None = None


class TaskReplace(BaseModel):
    title: str = Field(min_length=1)
    description: str
    completed: bool


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    completed: bool


@app.get("/")
async def root():
    return {"message": "Task Manager API"}


@app.get(
    "/tasks",
    response_model=list[TaskResponse]
)
async def get_tasks():
    tasks = service.get_tasks()

    return [task.to_dict() for task in tasks]


@app.get(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
async def get_task(task_id: int):
    task = service.find_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task.to_dict()


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_task(task_data: TaskCreate):
    task = service.create_task(
        task_data.title,
        task_data.description
    )

    save_tasks(service.get_tasks())

    return task.to_dict()


@app.put(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
async def replace_task(
    task_id: int,
    task_data: TaskReplace
):
    task = service.find_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task = service.update_task(
        task_id,
        task_data.title,
        task_data.description
    )

    task.completed = task_data.completed

    save_tasks(service.get_tasks())

    return task.to_dict()


@app.patch(
    "/tasks/{task_id}",
    response_model=TaskResponse
)
async def update_task(
    task_id: int,
    task_data: TaskUpdate
):
    task = service.find_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    update_data = task_data.model_dump(exclude_unset=True)

    if "title" in update_data:
        task.title = update_data["title"]

    if "description" in update_data:
        task.description = update_data["description"]

    if "completed" in update_data:
        task.completed = update_data["completed"]

    save_tasks(service.get_tasks())

    return task.to_dict()


@app.delete(
    "/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(task_id: int):
    deleted = service.delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    save_tasks(service.get_tasks())

    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )