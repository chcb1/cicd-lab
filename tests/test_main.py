import pytest
from fastapi.testclient import TestClient

from app import main


@pytest.fixture
def client():
    main._tasks.clear()
    return TestClient(main.app)


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version_defaults(client, monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)
    assert client.get("/version").json() == {"version": "dev", "environment": "local"}


def test_version_from_environment(client, monkeypatch):
    monkeypatch.setenv("APP_VERSION", "abc1234")
    monkeypatch.setenv("APP_ENV", "staging")
    assert client.get("/version").json() == {"version": "abc1234", "environment": "staging"}


def test_create_and_get_task(client):
    created = client.post("/tasks", json={"title": "Write the pipeline"})
    assert created.status_code == 201
    task = created.json()
    assert task["title"] == "Write the pipeline"
    assert task["done"] is False

    fetched = client.get(f"/tasks/{task['id']}")
    assert fetched.status_code == 200
    assert fetched.json() == task


def test_list_tasks(client):
    assert client.get("/tasks").json() == []
    client.post("/tasks", json={"title": "one"})
    client.post("/tasks", json={"title": "two", "done": True})
    assert [t["title"] for t in client.get("/tasks").json()] == ["one", "two"]


def test_create_task_rejects_empty_title(client):
    assert client.post("/tasks", json={"title": ""}).status_code == 422


def test_get_missing_task_returns_404(client):
    assert client.get("/tasks/999").status_code == 404


def test_delete_task(client):
    task_id = client.post("/tasks", json={"title": "temp"}).json()["id"]
    assert client.delete(f"/tasks/{task_id}").status_code == 204
    assert client.get(f"/tasks/{task_id}").status_code == 404


def test_delete_missing_task_returns_404(client):
    assert client.delete("/tasks/999").status_code == 404
