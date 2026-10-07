"""Task API - a deliberately small service used to practise CI/CD."""

import os
from itertools import count

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Task API")

# In-memory storage: state is lost on restart, which is fine for a pipeline lab.
_tasks: dict[int, dict] = {}
_ids = count(1)


class TaskIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    done: bool = False


class Task(TaskIn):
    id: int


@app.get("/health")
def health() -> dict:
    """Used by the Docker healthcheck and by the post-deploy smoke test."""
    return {"status": "ok"}


@app.get("/version")
def version() -> dict:
    """Shows which build is running. The pipeline injects these at build/deploy time."""
    return {
        "version": os.getenv("APP_VERSION", "dev"),
        "environment": os.getenv("APP_ENV", "local"),
    }


@app.get("/tasks", response_model=list[Task])
def list_tasks() -> list[dict]:
    return list(_tasks.values())


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskIn) -> dict:
    new = {"id": next(_ids), **task.model_dump()}
    _tasks[new["id"]] = new
    return new


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int) -> dict:
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return _tasks[task_id]


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int) -> None:
    if task_id not in _tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    del _tasks[task_id]
