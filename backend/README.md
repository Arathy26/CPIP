# Task Scheduler API

A single-user, headless REST API for managing tasks — create, retrieve, list, filter, update and delete. Built with Next.js App Router, Prisma ORM and PostgreSQL, and documented with Swagger/OpenAPI.

## Overview

This API is headless: there is no task-management frontend. Clients interact with it through REST endpoints and receive JSON. Each task has a status (`NEW`, `IN_PROGRESS`, `PENDING`, `COMPLETED`) and can optionally have a scheduled date and time. Scheduling only stores the planned time — it does not trigger automatic execution or notifications.

## Architecture

The app follows MVC adapted for a headless REST API, with clear separation of responsibilities:
Client / Swagger UI
↓
Route Handler (src/app/api/**/route.ts)
↓
Controller (src/controllers/)
↓
Service (src/services/)
↓
Model (src/models/)
↓
Prisma ORM (src/lib/prisma.ts)
↓
PostgreSQL


- **Route Handler** — receives the HTTP request and delegates to the controller. Contains no business logic or database queries.
- **Controller** — coordinates the request, invokes the service, and returns the HTTP response.
- **Service** — holds business rules, including the `completedAt` timestamp logic.
- **Validator** (`src/validators/`) — checks incoming data (title, status, UUIDs, timestamps, pagination, unsupported fields) before it reaches the service.
- **Model** — the only layer that talks to the database, via Prisma.
- **Swagger UI** (`/docs`) — documents and tests the API; it does not replace the API itself.

## Project structure
prisma/
schema.prisma # Database schema
migrations/ # Versioned schema changes
src/
app/
api/
tasks/route.ts # POST /api/tasks, GET /api/tasks
tasks/[id]/route.ts # GET/PATCH/DELETE /api/tasks/{id}
users/route.ts # User collection endpoint
users/[id]/route.ts # User item endpoint
openapi/route.ts # Serves the OpenAPI spec
docs/ # Swagger UI page
controllers/ # Coordinate requests and responses
services/ # Business rules
models/ # Database access via Prisma
validators/ # Input validation
lib/
prisma.ts # Shared Prisma client
tests/ # Automated tests


## Tech stack

- **Framework:** Next.js (App Router)
- **Database:** PostgreSQL
- **ORM:** Prisma
- **API docs:** Swagger UI / OpenAPI
- **Tests:** Jest

## Getting started

### Prerequisites

- Node.js
- Docker (for local PostgreSQL via `docker-compose`)

### Setup

```bash
# Install dependencies
npm install

# Copy environment variables and fill in your own values
cp .env.example .env

# Start PostgreSQL locally
docker compose up -d

# Apply database migrations
npx prisma migrate dev

# Start the development server
npm run dev
```

The API runs at `http://localhost:3000`.

### API documentation

- Swagger UI: `http://localhost:3000/docs`
- Raw OpenAPI spec: `http://localhost:3000/api/openapi`

### Database viewer

```bash
npx prisma studio
```

Opens at `http://localhost:5555`.

## API endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/tasks` | Create a task (defaults to status `NEW`) |
| GET | `/api/tasks` | List tasks, with filtering and pagination |
| GET | `/api/tasks/{id}` | Retrieve a single task |
| PATCH | `/api/tasks/{id}` | Partially update a task |
| DELETE | `/api/tasks/{id}` | Delete a task |

### Query parameters for GET /api/tasks

- `status` — filter by `NEW`, `IN_PROGRESS`, `PENDING` or `COMPLETED`
- `page`, `limit` — pagination

## Task fields

| Field | Type | Notes |
|---|---|---|
| id | UUID | Auto-generated |
| title | string | Required, 1–200 characters |
| description | text | Optional, up to 5,000 characters |
| status | enum | Defaults to `NEW` |
| scheduledAt | timestamp | Optional |
| completedAt | timestamp | Set automatically when status becomes `COMPLETED`, cleared otherwise |
| createdAt | timestamp | Set on creation |
| updatedAt | timestamp | Set on every update |

## Testing

```bash
npm test
```

Covers CRUD operations, status filtering, validation, missing tasks, and completion timestamp rules.

## Environment variables

See `.env.example` for the required variables, including `DATABASE_URL`. Never commit `.env` — it is excluded via `.gitignore`.
