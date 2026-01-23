# PronIELTS API Specification

## Base URL

- **Local Development**: `http://localhost:8000/api/v1`
- **Azure Development**: `https://pronielts-dev.azurewebsites.net/api/v1`
- **Production**: `https://pronielts.azurewebsites.net/api/v1`

## Authentication

### Mobile App
- No authentication required (MVP)
- User identified by `user_id` string (UUID generated on device)

### Web Admin
- **Type**: Bearer Token (JWT)
- **Header**: `Authorization: Bearer <token>`
- **Token Source**: Azure AD B2C
- **Token Expiration**: 1 hour

## Common Response Formats

### Success Response
```json
{
  "id": 1,
  "data": {...},
  "message": "Success"
}
```

### Error Response
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error

---

## Endpoints

### 1. Health Check

#### GET /health

Check API health status.

**Authentication**: None

**Response**:
```json
{
  "status": "healthy",
  "mock_mode": true,
  "version": "1.0.0"
}
```

---

### 2. Assessments

#### POST /assessments/assess

Submit audio for pronunciation assessment.

**Authentication**: None (user_id in body)

**Request**:
- **Content-Type**: `multipart/form-data`
- **Body Parameters**:
  - `audio` (file, required): Audio file (WAV, max 10MB)
  - `phrase_id` (integer, required): ID of phrase being assessed
  - `user_id` (string, required): Anonymous user identifier

**Example**:
```bash
curl -X POST \
  http://localhost:8000/api/v1/assessments/assess \
  -F "audio=@recording.wav" \
  -F "phrase_id=1" \
  -F "user_id=550e8400-e29b-41d4-a716-446655440000"
```

**Response** (200):
```json
{
  "id": 123,
  "user_id": 1,
  "phrase_id": 1,
  "scores": {
    "accuracy_score": 85.5,
    "prosody_score": 4.2,
    "fluency_score": 78.0,
    "completeness_score": 92.0,
    "overall_score": 84.9
  },
  "recognized_text": "Can you describe your experience with cloud computing?",
  "word_level_scores": {
    "Can": {
      "accuracy": 95.0,
      "error_type": "None"
    },
    "you": {
      "accuracy": 88.0,
      "error_type": "None"
    },
    "describe": {
      "accuracy": 72.0,
      "error_type": "Mispronunciation"
    }
  },
  "created_at": "2026-01-23T10:30:00Z"
}
```

**Error Responses**:
- `400`: Audio file too large or invalid format
- `404`: Phrase not found
- `500`: Assessment failed

---

### 3. Dialogs

#### GET /dialogs

List all dialogs, optionally filtered by category.

**Authentication**: None

**Query Parameters**:
- `category` (string, optional): Filter by category
  - Values: `Professional`, `Travel`, `General`, `Restaurant`, `IELTS_Part1`, `IELTS_Part2`, `IELTS_Part3`

**Example**:
```bash
curl http://localhost:8000/api/v1/dialogs?category=Professional
```

**Response** (200):
```json
[
  {
    "id": 1,
    "title": "Tech Job Interview",
    "category": "Professional",
    "description": "Common technical interview questions",
    "difficulty_level": "Advanced",
    "created_at": "2026-01-20T12:00:00Z",
    "phrases": [
      {
        "id": 1,
        "reference_text": "Can you describe your experience with cloud computing platforms like AWS or Azure?",
        "order": 1,
        "difficulty": "Advanced"
      },
      {
        "id": 2,
        "reference_text": "How do you approach debugging a complex software issue?",
        "order": 2,
        "difficulty": "Advanced"
      }
    ]
  }
]
```

---

#### GET /dialogs/{dialog_id}

Get a specific dialog with all phrases.

**Authentication**: None

**Path Parameters**:
- `dialog_id` (integer, required): Dialog ID

**Example**:
```bash
curl http://localhost:8000/api/v1/dialogs/1
```

**Response** (200):
```json
{
  "id": 1,
  "title": "Tech Job Interview",
  "category": "Professional",
  "description": "Common technical interview questions",
  "difficulty_level": "Advanced",
  "created_at": "2026-01-20T12:00:00Z",
  "updated_at": "2026-01-20T12:00:00Z",
  "phrases": [
    {
      "id": 1,
      "dialog_id": 1,
      "reference_text": "Can you describe your experience with cloud computing?",
      "order": 1,
      "phonetic_transcription": null,
      "difficulty": "Advanced"
    }
  ]
}
```

**Error Responses**:
- `404`: Dialog not found

---

#### POST /dialogs

Create a new dialog (Admin only).

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "title": "Business Meeting",
  "category": "Professional",
  "description": "Common phrases for business meetings",
  "difficulty_level": "Intermediate"
}
```

**Response** (201):
```json
{
  "id": 6,
  "title": "Business Meeting",
  "category": "Professional",
  "description": "Common phrases for business meetings",
  "difficulty_level": "Intermediate",
  "created_at": "2026-01-23T10:30:00Z"
}
```

**Error Responses**:
- `401`: Unauthorized
- `422`: Validation error

---

#### PUT /dialogs/{dialog_id}

Update an existing dialog (Admin only).

**Authentication**: Required (JWT)

**Path Parameters**:
- `dialog_id` (integer, required): Dialog ID

**Request Body**:
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response** (200):
```json
{
  "id": 1,
  "title": "Updated Title",
  "category": "Professional",
  "description": "Updated description",
  "difficulty_level": "Advanced",
  "updated_at": "2026-01-23T11:00:00Z"
}
```

---

#### DELETE /dialogs/{dialog_id}

Delete a dialog and all its phrases (Admin only).

**Authentication**: Required (JWT)

**Path Parameters**:
- `dialog_id` (integer, required): Dialog ID

**Response** (204): No content

**Error Responses**:
- `401`: Unauthorized
- `404`: Dialog not found

---

### 4. Phrases

#### GET /phrases/{phrase_id}

Get a specific phrase.

**Authentication**: None

**Path Parameters**:
- `phrase_id` (integer, required): Phrase ID

**Response** (200):
```json
{
  "id": 1,
  "dialog_id": 1,
  "reference_text": "Can you describe your experience with cloud computing?",
  "order": 1,
  "phonetic_transcription": "/kæn juː dɪˈskraɪb jɔːr ɪkˈspɪəriəns wɪð klaʊd kəmˈpjuːtɪŋ/",
  "difficulty": "Advanced"
}
```

---

#### POST /phrases

Create a new phrase (Admin only).

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "dialog_id": 1,
  "reference_text": "What programming languages are you proficient in?",
  "order": 6,
  "difficulty": "Intermediate"
}
```

**Response** (201):
```json
{
  "id": 26,
  "dialog_id": 1,
  "reference_text": "What programming languages are you proficient in?",
  "order": 6,
  "phonetic_transcription": null,
  "difficulty": "Intermediate"
}
```

---

#### PUT /phrases/{phrase_id}

Update an existing phrase (Admin only).

**Authentication**: Required (JWT)

**Path Parameters**:
- `phrase_id` (integer, required): Phrase ID

**Request Body**:
```json
{
  "reference_text": "Updated phrase text",
  "difficulty": "Beginner"
}
```

**Response** (200):
```json
{
  "id": 1,
  "dialog_id": 1,
  "reference_text": "Updated phrase text",
  "order": 1,
  "difficulty": "Beginner"
}
```

---

#### DELETE /phrases/{phrase_id}

Delete a phrase (Admin only).

**Authentication**: Required (JWT)

**Path Parameters**:
- `phrase_id` (integer, required): Phrase ID

**Response** (204): No content

---

### 5. Users

#### GET /users/me

Get current user information (Future).

**Authentication**: Required (JWT)

**Response** (200):
```json
{
  "id": 1,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2026-01-15T08:00:00Z"
}
```

---

#### GET /users/{user_id}/assessments

Get user's assessment history.

**Authentication**: None (MVP) / Required (Future)

**Path Parameters**:
- `user_id` (integer, required): User ID

**Query Parameters**:
- `limit` (integer, optional, default=50): Number of results
- `offset` (integer, optional, default=0): Pagination offset

**Response** (200):
```json
{
  "total": 150,
  "items": [
    {
      "id": 123,
      "phrase_id": 1,
      "phrase_text": "Can you describe your experience...",
      "overall_score": 84.9,
      "accuracy_score": 85.5,
      "prosody_score": 4.2,
      "fluency_score": 78.0,
      "created_at": "2026-01-23T10:30:00Z"
    }
  ]
}
```

---

#### GET /users/{user_id}/progress

Get user's progress statistics.

**Authentication**: None (MVP) / Required (Future)

**Path Parameters**:
- `user_id` (integer, required): User ID

**Response** (200):
```json
{
  "user_id": 1,
  "total_assessments": 150,
  "average_overall_score": 82.5,
  "average_accuracy": 84.0,
  "average_prosody": 4.1,
  "average_fluency": 79.5,
  "average_completeness": 88.0,
  "best_score": 95.5,
  "worst_score": 65.0,
  "categories_practiced": {
    "Professional": 50,
    "Travel": 30,
    "IELTS_Part1": 40,
    "General": 30
  },
  "improvement_rate": 1.2
}
```

---

### 6. Stats (Admin)

#### GET /stats

Get platform-wide statistics (Admin only).

**Authentication**: Required (JWT)

**Response** (200):
```json
{
  "total_users": 1250,
  "total_assessments": 15000,
  "assessments_today": 250,
  "average_overall_score": 78.5,
  "dialogs_count": 5,
  "phrases_count": 25,
  "popular_categories": [
    {
      "category": "IELTS_Part1",
      "count": 5000
    },
    {
      "category": "Professional",
      "count": 4000
    }
  ],
  "score_distribution": {
    "0-60": 1500,
    "60-75": 5000,
    "75-85": 6000,
    "85-100": 2500
  }
}
```

---

## Data Models

### Dialog

```json
{
  "id": "integer",
  "title": "string",
  "category": "string (enum)",
  "description": "string | null",
  "difficulty_level": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "phrases": "Phrase[]"
}
```

### Phrase

```json
{
  "id": "integer",
  "dialog_id": "integer",
  "reference_text": "string",
  "order": "integer",
  "phonetic_transcription": "string | null",
  "difficulty": "string"
}
```

### Assessment

```json
{
  "id": "integer",
  "user_id": "integer",
  "phrase_id": "integer",
  "accuracy_score": "float",
  "prosody_score": "float",
  "fluency_score": "float",
  "completeness_score": "float",
  "overall_score": "float",
  "word_level_scores": "object",
  "phoneme_level_scores": "object | null",
  "recognized_text": "string",
  "audio_blob_url": "string",
  "assessment_duration_seconds": "float",
  "created_at": "datetime"
}
```

### User

```json
{
  "id": "integer",
  "user_id": "string (UUID)",
  "email": "string | null",
  "full_name": "string | null",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## Rate Limiting

**Current (MVP)**: No rate limiting

**Future**:
- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Admin users: Unlimited

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1611234567
```

---

## Pagination

For endpoints returning lists, use query parameters:
- `limit`: Number of items per page (default: 50, max: 100)
- `offset`: Number of items to skip (default: 0)

**Response**:
```json
{
  "total": 150,
  "limit": 50,
  "offset": 0,
  "items": [...]
}
```

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| `AUDIO_TOO_LARGE` | Audio file exceeds 10MB | File size limit |
| `INVALID_AUDIO_FORMAT` | Unsupported audio format | Only WAV supported |
| `PHRASE_NOT_FOUND` | Phrase not found | Invalid phrase_id |
| `ASSESSMENT_FAILED` | Speech assessment failed | Azure SDK error |
| `INVALID_CATEGORY` | Invalid category | Not in enum list |
| `UNAUTHORIZED` | Authentication required | Missing/invalid JWT |

---

## WebSocket API (Future)

### WS /ws/assess

Real-time pronunciation feedback during recording.

**Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/assess?user_id=123&phrase_id=1');
```

**Messages**:
```json
// Client sends audio chunks
{
  "type": "audio_chunk",
  "data": "<base64-encoded-audio>"
}

// Server sends real-time feedback
{
  "type": "feedback",
  "word": "describe",
  "accuracy": 72.0,
  "error_type": "Mispronunciation"
}

// Server sends final assessment
{
  "type": "final_assessment",
  "assessment_id": 123,
  "scores": {...}
}
```

---

## SDK Examples

### Python (Backend)

```python
import requests

# Submit assessment
with open('recording.wav', 'rb') as audio_file:
    response = requests.post(
        'http://localhost:8000/api/v1/assessments/assess',
        files={'audio': audio_file},
        data={
            'phrase_id': 1,
            'user_id': '550e8400-e29b-41d4-a716-446655440000'
        }
    )

assessment = response.json()
print(f"Overall Score: {assessment['scores']['overall_score']}")
```

### Dart (Flutter)

```dart
import 'package:dio/dio.dart';

final dio = Dio(BaseOptions(baseUrl: 'http://localhost:8000/api/v1'));

// Get dialogs
final response = await dio.get('/dialogs', queryParameters: {'category': 'Professional'});
final dialogs = response.data as List;

// Submit assessment
final formData = FormData.fromMap({
  'audio': await MultipartFile.fromFile(audioPath),
  'phrase_id': 1,
  'user_id': userId,
});

final assessment = await dio.post('/assessments/assess', data: formData);
print('Score: ${assessment.data['scores']['overall_score']}');
```

### JavaScript (React)

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// Get dialogs
const { data: dialogs } = await api.get('/dialogs');

// Create dialog (admin)
const newDialog = await api.post('/dialogs', {
  title: 'Business Meeting',
  category: 'Professional',
  description: 'Common phrases',
  difficulty_level: 'Intermediate'
});
```

---

## Testing

### Interactive Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Postman Collection
Available in: `docs/postman/pronielts-api.json`

### cURL Examples
See `docs/curl-examples.md`

---

**Document Version**: 1.0
**Last Updated**: 2026-01-23
**OpenAPI Spec**: Available at `/openapi.json`
