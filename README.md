# Epic J3 – Developer Runbook / README

## Description

Create a comprehensive **Developer Runbook (README)** that enables a new developer (or the same team months later) to run the project from a clean checkout without requiring undocumented guidance.

The README should include:

- Project overview
- Prerequisites
- Repository cloning
- Backend setup
- Frontend setup
- Database setup
- Environment variables (.env)
- How to obtain required API keys
- Running the backend
- Running the frontend
- Running the database
- Running Ollama (if applicable)
- Loading test fixtures
- Executing the complete J2 Acceptance Flow
- Troubleshooting common issues

The guide should assume the reader has never worked on the project before.

---

## Prerequisites

- J2 – End-to-End Acceptance Flow

---

## Quality Attribute

### Maintainability

The README should allow any new developer to:

- Clone the repository
- Configure the environment
- Run every service
- Execute the entire project

without asking another developer for missing steps.

---

# Recommended README Structure

## 1. Project Overview

- Purpose
- Architecture
- Main Components
  - Backend
  - Frontend
  - Database
  - AI Models
  - Git Integration

---

## 2. Prerequisites

Required software:

- Git
- Python 3.11+
- Node.js
- Docker & Docker Compose
- PostgreSQL
- Ollama (optional)
- VS Code (recommended)

---

## 3. Clone Repository

```bash
git clone <repository-url>
cd <repository-name>
```

---

## 4. Backend Setup

Create virtual environment

```bash
python -m venv .venv
```

Activate

### Windows

```powershell
.venv\Scripts\activate
```

### Linux/macOS

```bash
source .venv/bin/activate
```

Install packages

```bash
pip install -r requirements.txt
```

---

## 5. Frontend Setup

```bash
cd frontend
npm install
```

---

## 6. Database Setup

Start database

```bash
docker compose up -d
```

Run migrations

```bash
alembic upgrade head
```

---

## 7. Environment Variables

Create a `.env` file.

Example:

```env
DATABASE_URL=

GITHUB_TOKEN=

ANTHROPIC_API_KEY=

LANGSMITH_API_KEY=

OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_MODEL=mistral:latest
```

### Environment Variables

| Variable | Purpose | Where to Get |
|----------|----------|--------------|
| DATABASE_URL | Database connection | Local PostgreSQL |
| GITHUB_TOKEN | GitHub API & PR creation | GitHub Personal Access Token |
| ANTHROPIC_API_KEY | Claude API | https://console.anthropic.com |
| LANGSMITH_API_KEY | LangSmith tracing | https://smith.langchain.com |
| OLLAMA_BASE_URL | Local Ollama server | Local installation |

---

## 8. Run Backend

```bash
uvicorn backend.main:app --reload
```

---

## 9. Run Frontend

```bash
npm run dev
```

---

## 10. Run Ollama

Start server

```bash
ollama serve
```

Download model

```bash
ollama pull mistral
```

---

## 11. Load Test Fixtures

Load the sample data from:

```
test-fixtures/
```

---

## 12. Manual J2 Acceptance Flow

1. Create a System
2. Upload Evidence
3. Trigger Ingestion
4. Wait until Job Status = Completed
5. Open Model Browser
6. Verify Evidence Citations
7. Verify Relationships
8. Verify Artifact Versions
9. Verify GitHub PR Links

---

## 13. Troubleshooting

Common Issues

- Missing environment variables
- Database connection failed
- Docker not running
- Ollama model not found
- GitHub authentication failed
- Frontend build failed

---

## 14. Useful Commands

Start backend

```bash
uvicorn backend.main:app --reload
```

Run tests

```bash
pytest
```

Start Docker

```bash
docker compose up
```

Stop Docker

```bash
docker compose down
```

Run frontend

```bash
npm run dev
```

---

# Definition of Done

J3 is complete when:

- A new developer clones the repository.
- Follows only the README.
- Installs all dependencies.
- Configures the environment.
- Starts the database.
- Starts the backend.
- Starts the frontend.
- Loads the test fixtures.
- Successfully executes the complete J2 Acceptance Flow.
- No undocumented steps or additional assistance are required.