# Agentic AI Architecture

## Overview
This repository contains the engineering codebase for the Agentic AI Architecture project.

## Project Structure

```text
backend/   # Backend services
agents/    # AI agents
frontend/  # Frontend application
```

## Tech Stack

- Python 3.11+
- PostgreSQL
- Docker & Docker Compose
- SQLAlchemy
- uv
- Ruff
- Black

## Environment Setup

1. Clone the repository.
2. Create a `.env` file from `.env.example`.
3. Install dependencies:

```bash
uv sync
```

4. Start the PostgreSQL database:

```bash
docker compose up
```

5. Run the application.

## Environment Variables

The project uses environment variables for configuration.

Required variables are documented in `.env.example`.

Example:

```env
DATABASE_URL=postgresql://app_user:password@localhost:5432/agentic_ai_db
```

## Code Quality

Run linting and formatting checks:

```powershell
.\lint.ps1
```

or

```bash
make lint
```

## Status

### Phase 1 - Epic A

- **A1:** Repository & Python Environment Scaffolding
- **A2:** PostgreSQL Database Setup (Local Development)

### A2 Highlights

- Local PostgreSQL database using Docker Compose.
- Dedicated application database user (non-superuser).
- Database connection configured through `DATABASE_URL`.
- Environment variables managed using `.env`.
- `.env.example` provided with placeholder values.
- Reproducible local development environment using Docker Compose.