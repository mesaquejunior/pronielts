# PronIELTS Content Automation - Integration Document

## 1. Overview

This document describes how the automation pipeline integrates with the PronIELTS platform, including API contracts, data mapping, and synchronization strategies.

---

## 2. Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         INTEGRATION ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐          ┌─────────────────────────────────┐
│     AUTOMATION PIPELINE         │          │         PRONIELTS PLATFORM      │
│                                 │          │                                 │
│  ┌───────────────────────────┐  │          │  ┌───────────────────────────┐  │
│  │   Exporter Service        │  │  HTTP    │  │   FastAPI Backend         │  │
│  │                           │──┼──────────┼─▶│                           │  │
│  │   • Batch dialogues       │  │  POST    │  │   POST /api/v1/admin/     │  │
│  │   • Map CEFR → difficulty │  │          │  │        bulk-import        │  │
│  │   • Validate payload      │  │          │  │                           │  │
│  │   • Handle retries        │  │          │  │   • Validate request      │  │
│  └───────────────────────────┘  │          │  │   • Create categories     │  │
│                                 │          │  │   • Insert dialogues      │  │
│  ┌───────────────────────────┐  │          │  │   • Insert phrases        │  │
│  │   Automation PostgreSQL   │  │          │  └───────────────────────────┘  │
│  │                           │  │          │               │                 │
│  │   • generated_phrases     │  │          │               ▼                 │
│  │   • generated_dialogues   │  │          │  ┌───────────────────────────┐  │
│  │   • export_history        │  │          │  │   PronIELTS PostgreSQL    │  │
│  └───────────────────────────┘  │          │  │                           │  │
│               │                 │          │  │   • categories            │  │
│               │                 │          │  │   • dialogs               │  │
│               ▼                 │          │  │   • phrases               │  │
│  ┌───────────────────────────┐  │          │  │   • assessments           │  │
│  │   Sync Status Tracker     │  │  HTTP    │  └───────────────────────────┘  │
│  │                           │◀─┼──────────┼──│                              │
│  │   • Track exported IDs    │  │  Response│  │                              │
│  │   • Mark synced records   │  │          │  │                              │
│  └───────────────────────────┘  │          │  │                              │
└─────────────────────────────────┘          └─────────────────────────────────┘
```

---

## 3. Bulk Import API Specification

### 3.1 New Endpoint (To Be Implemented in PronIELTS)

**Endpoint:** `POST /api/v1/admin/bulk-import`

**Authentication:** JWT Bearer Token (Admin role required)

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: application/json
X-Batch-Id: <unique_batch_identifier>
```

**Request Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["dialogues", "source", "batch_id"],
  "properties": {
    "dialogues": {
      "type": "array",
      "minItems": 1,
      "maxItems": 50,
      "items": {
        "type": "object",
        "required": ["title", "category_name", "difficulty_level", "phrases"],
        "properties": {
          "title": {
            "type": "string",
            "minLength": 5,
            "maxLength": 200
          },
          "category_name": {
            "type": "string",
            "enum": [
              "Professional",
              "Travel",
              "Restaurant",
              "General",
              "Technology",
              "Health",
              "Education",
              "Entertainment",
              "IELTS_Part1",
              "IELTS_Part2",
              "IELTS_Part3"
            ]
          },
          "difficulty_level": {
            "type": "string",
            "enum": ["beginner", "intermediate", "advanced"]
          },
          "description": {
            "type": "string",
            "maxLength": 500
          },
          "accent": {
            "type": "string",
            "enum": ["american", "british", "australian", "south_african", "irish", "scottish"]
          },
          "phrases": {
            "type": "array",
            "minItems": 2,
            "maxItems": 12,
            "items": {
              "type": "object",
              "required": ["reference_text", "order"],
              "properties": {
                "reference_text": {
                  "type": "string",
                  "minLength": 5,
                  "maxLength": 500
                },
                "order": {
                  "type": "integer",
                  "minimum": 1
                },
                "difficulty": {
                  "type": "string",
                  "enum": ["beginner", "intermediate", "advanced"]
                },
                "phonetic_transcription": {
                  "type": "string"
                },
                "speaker": {
                  "type": "string",
                  "enum": ["A", "B"]
                }
              }
            }
          }
        }
      }
    },
    "source": {
      "type": "string",
      "description": "Identifier for the content source"
    },
    "batch_id": {
      "type": "string",
      "pattern": "^batch-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$"
    }
  }
}
```

**Example Request:**
```json
{
  "dialogues": [
    {
      "title": "Making a Restaurant Reservation",
      "category_name": "Restaurant",
      "difficulty_level": "intermediate",
      "description": "Practice making reservations at restaurants using polite language",
      "accent": "british",
      "phrases": [
        {
          "reference_text": "Good evening, I'd like to make a reservation please.",
          "order": 1,
          "difficulty": "intermediate",
          "speaker": "A"
        },
        {
          "reference_text": "Certainly, sir. For how many people and what time?",
          "order": 2,
          "difficulty": "intermediate",
          "speaker": "B"
        },
        {
          "reference_text": "It's for two people at seven thirty, if possible.",
          "order": 3,
          "difficulty": "intermediate",
          "speaker": "A"
        },
        {
          "reference_text": "Let me check our availability. Yes, we have a table available.",
          "order": 4,
          "difficulty": "intermediate",
          "speaker": "B"
        },
        {
          "reference_text": "Wonderful! Could we have a table by the window?",
          "order": 5,
          "difficulty": "intermediate",
          "speaker": "A"
        },
        {
          "reference_text": "I'll make a note of that. May I have your name, please?",
          "order": 6,
          "difficulty": "intermediate",
          "speaker": "B"
        }
      ]
    }
  ],
  "source": "automation-pipeline",
  "batch_id": "batch-2024-01-15-103045"
}
```

**Success Response (201 Created):**
```json
{
  "success": true,
  "batch_id": "batch-2024-01-15-103045",
  "imported": {
    "dialogues": 1,
    "phrases": 6,
    "categories_created": 0
  },
  "results": [
    {
      "title": "Making a Restaurant Reservation",
      "dialog_id": 42,
      "phrase_ids": [256, 257, 258, 259, 260, 261]
    }
  ],
  "processed_at": "2024-01-15T10:30:47Z"
}
```

**Error Responses:**

**400 Bad Request:**
```json
{
  "success": false,
  "error": "validation_error",
  "message": "Invalid request payload",
  "details": [
    {
      "field": "dialogues[0].phrases[2].reference_text",
      "error": "String too short (minimum 5 characters)"
    }
  ]
}
```

**409 Conflict (Duplicate Batch):**
```json
{
  "success": false,
  "error": "duplicate_batch",
  "message": "Batch batch-2024-01-15-103045 has already been processed",
  "original_import": {
    "imported_at": "2024-01-15T10:30:47Z",
    "dialogues": 1
  }
}
```

**500 Internal Server Error:**
```json
{
  "success": false,
  "error": "internal_error",
  "message": "An unexpected error occurred",
  "request_id": "req-abc123"
}
```

---

## 4. Data Mapping

### 4.1 CEFR to Difficulty Mapping

| CEFR Level | PronIELTS Difficulty | Description |
|------------|---------------------|-------------|
| A1 | beginner | Basic phrases, simple structures |
| A2 | beginner | Everyday expressions, simple sentences |
| B1 | intermediate | Common topics, basic tenses |
| B2 | intermediate | Complex sentences, abstract topics |
| C1 | advanced | Sophisticated language, implicit meaning |
| C2 | advanced | Full mastery, nuance, idiomatic |

### 4.2 Category Mapping

| Automation Category | PronIELTS Category | Notes |
|--------------------|-------------------|-------|
| professional | Professional | Business, workplace |
| travel | Travel | Tourism, transportation |
| restaurant | Restaurant | Food, dining |
| general | General | Everyday conversations |
| news | General | News mapped to general |
| technology | Technology | Tech-related topics |
| health | Health | Medical, wellness |
| education | Education | Academic contexts |
| entertainment | Entertainment | Leisure, hobbies |
| ielts_part1 | IELTS_Part1 | Introduction, familiar topics |
| ielts_part2 | IELTS_Part2 | Long turn, individual topic |
| ielts_part3 | IELTS_Part3 | Two-way discussion |

### 4.3 Accent Preservation

The automation pipeline captures accent information per source. This is preserved in the dialogue metadata:

```python
ACCENT_MAPPING = {
    "american": "american",
    "us": "american",
    "british": "british",
    "uk": "british",
    "australian": "australian",
    "au": "australian",
    "south_african": "south_african",
    "za": "south_african",
    "irish": "irish",
    "scottish": "scottish"
}
```

---

## 5. Backend Implementation Guide

### 5.1 New Files to Create

```
backend/app/
├── api/v1/endpoints/
│   └── bulk_import.py          # New endpoint
├── schemas/
│   └── bulk_import.py          # Request/response schemas
├── services/
│   └── bulk_import_service.py  # Business logic
└── models/
    └── import_batch.py         # Import tracking model
```

### 5.2 Database Migration

```sql
-- alembic migration: add import tracking
CREATE TABLE import_batches (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,
    source VARCHAR(100) NOT NULL,
    dialogues_count INTEGER NOT NULL DEFAULT 0,
    phrases_count INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'completed',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_import_batches_batch_id ON import_batches(batch_id);
CREATE INDEX idx_import_batches_source ON import_batches(source);
CREATE INDEX idx_import_batches_created_at ON import_batches(created_at DESC);

-- Add source tracking to dialogs
ALTER TABLE dialogs ADD COLUMN source VARCHAR(100);
ALTER TABLE dialogs ADD COLUMN import_batch_id INTEGER REFERENCES import_batches(id);
ALTER TABLE dialogs ADD COLUMN accent VARCHAR(50);

CREATE INDEX idx_dialogs_source ON dialogs(source);
CREATE INDEX idx_dialogs_accent ON dialogs(accent);
```

### 5.3 Pydantic Schemas

```python
# backend/app/schemas/bulk_import.py
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class CategoryName(str, Enum):
    PROFESSIONAL = "Professional"
    TRAVEL = "Travel"
    RESTAURANT = "Restaurant"
    GENERAL = "General"
    TECHNOLOGY = "Technology"
    HEALTH = "Health"
    EDUCATION = "Education"
    ENTERTAINMENT = "Entertainment"
    IELTS_PART1 = "IELTS_Part1"
    IELTS_PART2 = "IELTS_Part2"
    IELTS_PART3 = "IELTS_Part3"

class AccentType(str, Enum):
    AMERICAN = "american"
    BRITISH = "british"
    AUSTRALIAN = "australian"
    SOUTH_AFRICAN = "south_african"
    IRISH = "irish"
    SCOTTISH = "scottish"

class BulkPhraseCreate(BaseModel):
    reference_text: str = Field(..., min_length=5, max_length=500)
    order: int = Field(..., ge=1)
    difficulty: Optional[DifficultyLevel] = None
    phonetic_transcription: Optional[str] = None
    speaker: Optional[str] = Field(None, pattern="^[AB]$")

class BulkDialogCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    category_name: CategoryName
    difficulty_level: DifficultyLevel
    description: Optional[str] = Field(None, max_length=500)
    accent: Optional[AccentType] = None
    phrases: List[BulkPhraseCreate] = Field(..., min_items=2, max_items=12)

    @validator('phrases')
    def validate_phrase_order(cls, v):
        orders = [p.order for p in v]
        if orders != list(range(1, len(v) + 1)):
            raise ValueError('Phrases must have consecutive order starting from 1')
        return v

class BulkImportRequest(BaseModel):
    dialogues: List[BulkDialogCreate] = Field(..., min_items=1, max_items=50)
    source: str
    batch_id: str = Field(..., pattern="^batch-[0-9]{4}-[0-9]{2}-[0-9]{2}-[0-9]{6}$")

class BulkDialogResult(BaseModel):
    title: str
    dialog_id: int
    phrase_ids: List[int]

class BulkImportResponse(BaseModel):
    success: bool
    batch_id: str
    imported: dict
    results: List[BulkDialogResult]
    processed_at: str
```

### 5.4 Service Implementation

```python
# backend/app/services/bulk_import_service.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models import Dialog, Phrase, Category, ImportBatch
from app.schemas.bulk_import import BulkImportRequest, BulkImportResponse
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BulkImportService:
    def __init__(self, db: Session):
        self.db = db

    async def import_dialogues(self, request: BulkImportRequest) -> BulkImportResponse:
        # Check for duplicate batch
        existing_batch = self.db.query(ImportBatch).filter(
            ImportBatch.batch_id == request.batch_id
        ).first()

        if existing_batch:
            raise DuplicateBatchError(
                batch_id=request.batch_id,
                original_import=existing_batch
            )

        # Create import batch record
        import_batch = ImportBatch(
            batch_id=request.batch_id,
            source=request.source,
            status="processing"
        )
        self.db.add(import_batch)
        self.db.flush()

        results = []
        total_dialogues = 0
        total_phrases = 0
        categories_created = 0

        try:
            for dialog_data in request.dialogues:
                # Get or create category
                category = self._get_or_create_category(dialog_data.category_name)
                if category._created:
                    categories_created += 1

                # Create dialog
                dialog = Dialog(
                    title=dialog_data.title,
                    category_id=category.id,
                    description=dialog_data.description,
                    difficulty_level=dialog_data.difficulty_level.value,
                    source=request.source,
                    import_batch_id=import_batch.id,
                    accent=dialog_data.accent.value if dialog_data.accent else None
                )
                self.db.add(dialog)
                self.db.flush()

                # Create phrases
                phrase_ids = []
                for phrase_data in dialog_data.phrases:
                    phrase = Phrase(
                        dialog_id=dialog.id,
                        reference_text=phrase_data.reference_text,
                        order=phrase_data.order,
                        difficulty=phrase_data.difficulty.value if phrase_data.difficulty else dialog_data.difficulty_level.value,
                        phonetic_transcription=phrase_data.phonetic_transcription
                    )
                    self.db.add(phrase)
                    self.db.flush()
                    phrase_ids.append(phrase.id)

                results.append({
                    "title": dialog_data.title,
                    "dialog_id": dialog.id,
                    "phrase_ids": phrase_ids
                })

                total_dialogues += 1
                total_phrases += len(phrase_ids)

            # Update batch record
            import_batch.status = "completed"
            import_batch.dialogues_count = total_dialogues
            import_batch.phrases_count = total_phrases

            self.db.commit()

            return BulkImportResponse(
                success=True,
                batch_id=request.batch_id,
                imported={
                    "dialogues": total_dialogues,
                    "phrases": total_phrases,
                    "categories_created": categories_created
                },
                results=results,
                processed_at=datetime.utcnow().isoformat() + "Z"
            )

        except Exception as e:
            self.db.rollback()
            import_batch.status = "failed"
            import_batch.error_message = str(e)
            self.db.commit()
            raise

    def _get_or_create_category(self, category_name: str) -> Category:
        category = self.db.query(Category).filter(
            Category.name == category_name
        ).first()

        if category:
            category._created = False
            return category

        category = Category(
            name=category_name,
            description=f"Auto-created category for {category_name}"
        )
        category._created = True
        self.db.add(category)
        self.db.flush()
        return category
```

### 5.5 API Endpoint

```python
# backend/app/api/v1/endpoints/bulk_import.py
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.bulk_import import BulkImportRequest, BulkImportResponse
from app.services.bulk_import_service import BulkImportService, DuplicateBatchError
from app.api.deps import get_current_admin_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/bulk-import",
    response_model=BulkImportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Bulk import dialogues and phrases",
    description="Import multiple dialogues with their phrases in a single transaction"
)
async def bulk_import(
    request: BulkImportRequest,
    x_batch_id: str = Header(None, alias="X-Batch-Id"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """
    Bulk import dialogues from the automation pipeline.

    Requires admin authentication.

    - **dialogues**: List of dialogues to import (max 50)
    - **source**: Identifier for the content source
    - **batch_id**: Unique batch identifier for idempotency
    """
    # Validate batch_id matches header if provided
    if x_batch_id and x_batch_id != request.batch_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Batch-Id header does not match batch_id in body"
        )

    service = BulkImportService(db)

    try:
        result = await service.import_dialogues(request)
        logger.info(
            f"Bulk import successful: batch={request.batch_id}, "
            f"dialogues={result.imported['dialogues']}, "
            f"phrases={result.imported['phrases']}"
        )
        return result

    except DuplicateBatchError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "duplicate_batch",
                "message": f"Batch {e.batch_id} has already been processed",
                "original_import": {
                    "imported_at": e.original_import.created_at.isoformat(),
                    "dialogues": e.original_import.dialogues_count
                }
            }
        )

    except Exception as e:
        logger.error(f"Bulk import failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during import"
        )
```

---

## 6. Exporter Service (Automation Side)

### 6.1 Implementation

```python
# automation/services/exporter.py
import httpx
from datetime import datetime
from typing import List
import structlog

logger = structlog.get_logger()

CEFR_TO_DIFFICULTY = {
    "A1": "beginner",
    "A2": "beginner",
    "B1": "intermediate",
    "B2": "intermediate",
    "C1": "advanced",
    "C2": "advanced"
}

class PronIELTSExporter:
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }
        )

    async def export_dialogues(self, dialogues: List[dict]) -> dict:
        """Export dialogues to PronIELTS platform."""
        batch_id = f"batch-{datetime.now().strftime('%Y-%m-%d-%H%M%S')}"

        payload = {
            "dialogues": [
                self._transform_dialogue(d) for d in dialogues
            ],
            "source": "automation-pipeline",
            "batch_id": batch_id
        }

        logger.info("exporting_dialogues", batch_id=batch_id, count=len(dialogues))

        try:
            response = await self.client.post(
                f"{self.base_url}/api/v1/admin/bulk-import",
                json=payload,
                headers={"X-Batch-Id": batch_id}
            )

            if response.status_code == 201:
                result = response.json()
                logger.info(
                    "export_successful",
                    batch_id=batch_id,
                    dialogues=result["imported"]["dialogues"],
                    phrases=result["imported"]["phrases"]
                )
                return result

            elif response.status_code == 409:
                logger.warning("duplicate_batch", batch_id=batch_id)
                raise DuplicateBatchError(batch_id)

            else:
                logger.error(
                    "export_failed",
                    batch_id=batch_id,
                    status=response.status_code,
                    response=response.text
                )
                raise ExportError(f"Export failed: {response.status_code}")

        except httpx.RequestError as e:
            logger.error("export_request_error", batch_id=batch_id, error=str(e))
            raise

    def _transform_dialogue(self, dialogue: dict) -> dict:
        """Transform automation dialogue format to PronIELTS format."""
        return {
            "title": dialogue["title"],
            "category_name": dialogue["category"].title().replace("_", ""),
            "difficulty_level": CEFR_TO_DIFFICULTY[dialogue["cefr_level"]],
            "description": f"CEFR {dialogue['cefr_level']} - {dialogue['category'].title()} conversation",
            "accent": dialogue.get("accent"),
            "phrases": [
                {
                    "reference_text": turn["text"],
                    "order": turn["order"],
                    "difficulty": CEFR_TO_DIFFICULTY[dialogue["cefr_level"]],
                    "speaker": turn.get("speaker")
                }
                for turn in dialogue["turns"]
            ]
        }

    async def close(self):
        await self.client.aclose()


class ExportError(Exception):
    pass


class DuplicateBatchError(ExportError):
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        super().__init__(f"Batch {batch_id} already processed")
```

### 6.2 Airflow Task

```python
# automation/dags/tasks/export_task.py
from airflow.decorators import task
from automation.services.exporter import PronIELTSExporter
import os

@task
async def export_to_pronielts(validated_dialogues: List[dict]) -> dict:
    """Export validated dialogues to PronIELTS."""
    if not validated_dialogues:
        return {"exported": 0, "skipped": "no dialogues"}

    exporter = PronIELTSExporter(
        base_url=os.environ["PRONIELTS_API_URL"],
        api_token=os.environ["PRONIELTS_API_TOKEN"]
    )

    try:
        result = await exporter.export_dialogues(validated_dialogues)
        return {
            "exported": result["imported"]["dialogues"],
            "batch_id": result["batch_id"],
            "phrase_count": result["imported"]["phrases"]
        }
    finally:
        await exporter.close()
```

---

## 7. Idempotency & Error Handling

### 7.1 Batch Tracking

Each export uses a unique batch_id to ensure idempotency:

```
batch-YYYY-MM-DD-HHMMSS
```

If a batch is re-sent (e.g., due to network timeout), the API returns 409 Conflict instead of duplicating data.

### 7.2 Retry Strategy

```python
# automation/config/retry.py
EXPORT_RETRY_CONFIG = {
    "max_retries": 3,
    "retry_delay_seconds": [60, 120, 300],  # 1min, 2min, 5min
    "retry_on_status_codes": [502, 503, 504],  # Gateway errors
    "no_retry_on_status_codes": [400, 401, 403, 409]  # Client errors
}
```

### 7.3 Dead Letter Queue

Failed exports are logged for manual review:

```sql
-- automation database
CREATE TABLE export_failures (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) NOT NULL,
    dialogue_ids UUID[] NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    error_message TEXT,
    payload JSONB NOT NULL,
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);
```

---

## 8. Monitoring & Alerts

### 8.1 Metrics to Track

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| `export_success_total` | Successful exports | - |
| `export_failure_total` | Failed exports | > 0 |
| `export_latency_seconds` | Export duration | > 30s |
| `export_dialogues_total` | Dialogues exported | - |
| `export_batch_size` | Dialogues per batch | > 50 |

### 8.2 Alerts

```yaml
# prometheus alerting rules
groups:
  - name: pronielts-export
    rules:
      - alert: ExportFailure
        expr: increase(export_failure_total[5m]) > 0
        for: 1m
        labels:
          severity: warning
        annotations:
          summary: "PronIELTS export failure"
          description: "Export to PronIELTS failed in the last 5 minutes"

      - alert: ExportLatencyHigh
        expr: export_latency_seconds > 30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High export latency"
          description: "Export latency exceeded 30 seconds"
```

---

## 9. Testing Integration

### 9.1 Integration Test

```python
# tests/integration/test_bulk_import.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_bulk_import_success():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/admin/bulk-import",
            json={
                "dialogues": [
                    {
                        "title": "Test Dialogue",
                        "category_name": "General",
                        "difficulty_level": "intermediate",
                        "phrases": [
                            {"reference_text": "Hello, how are you?", "order": 1},
                            {"reference_text": "I'm fine, thank you.", "order": 2}
                        ]
                    }
                ],
                "source": "test",
                "batch_id": "batch-2024-01-15-100000"
            },
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 201
        data = response.json()
        assert data["success"] is True
        assert data["imported"]["dialogues"] == 1
        assert data["imported"]["phrases"] == 2


@pytest.mark.asyncio
async def test_bulk_import_duplicate_batch():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # First import
        await client.post(
            "/api/v1/admin/bulk-import",
            json={...},
            headers={"Authorization": "Bearer test-token"}
        )

        # Duplicate import
        response = await client.post(
            "/api/v1/admin/bulk-import",
            json={...},  # Same batch_id
            headers={"Authorization": "Bearer test-token"}
        )

        assert response.status_code == 409
        assert response.json()["error"] == "duplicate_batch"
```

---

## 10. Rollout Plan

### Phase 1: API Development (PronIELTS Backend)
1. Create bulk_import schemas
2. Create ImportBatch model and migration
3. Implement BulkImportService
4. Create /bulk-import endpoint
5. Add integration tests
6. Deploy to staging

### Phase 2: Exporter Development (Automation)
1. Implement PronIELTSExporter service
2. Add Airflow export task
3. Configure environment variables
4. Test against staging API
5. Add monitoring metrics

### Phase 3: End-to-End Testing
1. Run full pipeline with test content
2. Verify dialogues appear in PronIELTS
3. Test mobile app with new dialogues
4. Validate pronunciation assessment works

### Phase 4: Production Deployment
1. Deploy PronIELTS API changes
2. Configure production credentials
3. Enable Airflow export task
4. Monitor first batch
5. Verify data integrity
