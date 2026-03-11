# Ticket API

Mini REST API for ticket management built with FastAPI, SQLAlchemy, and SQLite (in-memory).

## Features

- Create, list, get, update, and close tickets
- Ticket status: `open`, `stalled`, `closed`
- Swagger documentation at `/docs`
- In-memory SQLite (no persistence after restart)

## Requirements

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (package manager)

## Install uv

Install `uv` by following the official documentation (covers Linux/macOS/Windows):
[uv installation guide](https://docs.astral.sh/uv/getting-started/installation/).

If you prefer, you can also run this project using Docker (see below) without installing `uv`.

## Installation

Using a virtual environment (recommended, to avoid affecting your system):

```bash
uv venv
uv sync
```

`uv venv` creates a `.venv` in the project; `uv sync` installs dependencies into it.

You do not need to activate the virtual environment when using `uv run` (it will use the project `.venv` automatically).

Install development dependencies (tests, linting, pre-commit):

```bash
uv sync --group dev
```

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

API available at `http://127.0.0.1:8000`. Swagger UI at `http://127.0.0.1:8000/docs`.

## Run tests

```bash
uv run pytest
```

With coverage:

```bash
uv run pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

## Pre-commit (Ruff + ty on commit)

This project includes a `.pre-commit-config.yaml` that runs Ruff (with auto-fix), `ty` (static type checker), and a few basic checks before each commit.

```bash
uv run pre-commit install
uv run pre-commit run --all-files
```

You can also run type checking manually:

```bash
uv run ty check
```

## Docker

Prerequisites: Docker installed and running (Docker Compose is included in modern Docker installations).
See [Docker installation](https://docs.docker.com/get-docker/).

```bash
docker compose up --build
```

API available at `http://localhost:8000`.

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| POST | /tickets/ | Create a ticket |
| GET | /tickets/ | List all tickets |
| GET | /tickets/{id} | Get a ticket |
| PUT | /tickets/{id} | Update a ticket |
| PATCH | /tickets/{id}/close | Close a ticket |


## Manual API scenarios

To exercise the API with realistic data (create, list, get, update, close), run the scenario script. Start the API first, then in another terminal:

The script below should work, no matter if you run the API locally or with docker compose.

```bash
uv run python -m tests.manual_api_scenarios
```
