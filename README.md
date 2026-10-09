# cicd-lab

A small FastAPI service (Task API) used to practise a full CI/CD pipeline with
GitHub Actions. The app is intentionally trivial; the pipeline is the point.
teste

## What is in here

| Path | Purpose |
|---|---|
| `app/main.py` | The API: `/health`, `/version`, and CRUD on `/tasks` |
| `tests/` | Unit tests (pytest), 100% coverage to start with |
| `pyproject.toml` | Ruff (lint/format) and pytest settings; build fails under 80% coverage |
| `Dockerfile` | The image that becomes the deployable artifact |
| `.github/workflows/ci.yml` | Phase 1 pipeline: lint, test, build the image, smoke test it |

## Run it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt

ruff check . && ruff format --check .   # lint and formatting
pytest                                  # tests with coverage
uvicorn app.main:app --reload           # http://localhost:8000/docs
```

With Docker:

```bash
docker build --build-arg APP_VERSION=local-test -t task-api:local .
docker run --rm -p 8000:8000 task-api:local
curl localhost:8000/version
```

## Put it on GitHub

```bash
git init -b main
git add .
git commit -m "Initial commit: Task API with CI"
gh repo create cicd-lab --private --source=. --push
```

The first push triggers the workflow; watch it under the **Actions** tab.

## Phase 1 exercises

1. **Protect main.** Settings > Branches > add a rule for `main`: require a pull
   request and require the status checks `Lint and test` and
   `Build image (no push yet)`. From now on, nothing reaches main without a green pipeline.
2. **Break the tests.** On a branch, change `{"status": "ok"}` to `{"status": "up"}`
   in `app/main.py`, open a PR, and confirm the merge is blocked.
3. **Break the lint.** Add an unused `import json` and see which step fails.
4. **Break the coverage gate.** Add a new endpoint without a test until coverage
   drops below 80%.
5. **Add a feature properly.** Implement `PUT /tasks/{id}` to mark a task done,
   with tests, through a PR.

## Next phases

- **Phase 2:** SonarQube Cloud quality gate, Trivy scan, push the image to GHCR tagged with the commit SHA
- **Phase 3:** self-hosted runner on the Ubuntu machine, automatic deploy to staging
- **Phase 4:** manual approval, then promote the same image to prod
