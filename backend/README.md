# PronIELTS Backend API

FastAPI backend for the IELTS Pronunciation Assessment Platform.

## Setup

1. Install dependencies:
```bash
poetry install
```

2. Create `.env` file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run database migrations:
```bash
poetry run alembic upgrade head
```

4. Seed database:
```bash
psql -h localhost -U pronielts -d pronielts -f ../infrastructure/scripts/seed_database.sql
```

5. Start development server:
```bash
poetry run uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

## Development

Run tests:
```bash
poetry run pytest
```

Format code:
```bash
poetry run black app/
```

Lint code:
```bash
poetry run pylint app/
```

## Environment Variables

See `.env.example` for required configuration.

**Mock Mode**: Set `MOCK_MODE=true` for local development without Azure services.
