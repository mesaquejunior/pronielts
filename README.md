# PronIELTS - IELTS Pronunciation Assessment Platform

A comprehensive pronunciation assessment platform for IELTS learners, featuring AI-powered speech evaluation using Azure Cognitive Services.

## Overview

PronIELTS is a multi-platform application designed to help English learners improve their pronunciation through IELTS-style speaking practice. The platform provides detailed feedback on accuracy, prosody, fluency, and completeness using Azure Speech SDK.

### Key Features

- 🎤 **Real-time Pronunciation Assessment**: Get instant feedback on your pronunciation
- 📊 **Detailed Metrics**: Track accuracy, prosody, fluency, and completeness scores
- 📱 **Mobile App**: Practice on iOS and Android devices
- 💻 **Web Admin Panel**: Manage content and view analytics
- 🌐 **Offline Support**: Practice even without internet connection
- 🎯 **IELTS-focused Content**: Specialized dialogues for IELTS preparation

### Target Scores

- **Accuracy**: % phonemes/words correct (IELTS Band correlation)
- **Prosody**: Rhythm/intonation score (0-5)
- **Fluency**: Pauses/speed (words/min)
- **Completeness**: % reference text recognized
- **Overall Score**: Aggregated score (0-100)

## Architecture

```
Flutter Mobile ──POST /assess──> FastAPI Backend (Azure App Service)
                          │
                          ├── Azure Speech Batch API
                          ├── Azure SQL Database (scores, dialogs)
                          └── Blob Storage (encrypted audio)
React Web Admin ──Azure AD B2C──> Backend (CRUD)
```

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: Azure SQL Database (PostgreSQL for local dev)
- **Cloud Services**: Azure Speech SDK, Blob Storage, Key Vault
- **ORM**: SQLAlchemy
- **Migrations**: Alembic

#### Mobile
- **Framework**: Flutter 3.x
- **State Management**: Provider
- **Local Storage**: Hive
- **Audio**: record, audioplayers packages

#### Web Admin
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **Authentication**: Azure AD B2C (MSAL)
- **State Management**: React Query
- **Charts**: Chart.js

#### Infrastructure
- **IaC**: Terraform
- **CI/CD**: GitHub Actions
- **Hosting**: Azure (Free Tier initially)

## Project Structure

```
pronielts/
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Configuration
│   │   ├── db/           # Database setup
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── tests/        # Tests
│   ├── alembic/          # Database migrations
│   └── requirements.txt
│
├── mobile/               # Flutter application
│   ├── lib/
│   │   ├── config/       # App configuration
│   │   ├── models/       # Data models
│   │   ├── services/     # API, audio, offline queue
│   │   ├── providers/    # State management
│   │   ├── screens/      # UI screens
│   │   └── widgets/      # Reusable widgets
│   └── pubspec.yaml
│
├── web/                  # React admin panel
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── services/     # API client
│   │   ├── hooks/        # Custom hooks
│   │   ├── pages/        # Page components
│   │   ├── types/        # TypeScript types
│   │   └── config/       # Azure AD config
│   └── package.json
│
├── infrastructure/       # Terraform & scripts
│   ├── terraform/
│   │   ├── modules/      # Reusable modules
│   │   └── environments/ # Environment configs
│   └── scripts/          # Setup & seed scripts
│
├── docs/                 # Documentation
├── .github/workflows/    # CI/CD pipelines
├── docker-compose.yml    # Local development
└── IMPLEMENTATION_TRACKER.md
```

## Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **Flutter**: 3.0 or higher
- **Docker**: For local development
- **PostgreSQL**: 15 (via Docker)
- **Terraform**: 1.6+ (for infrastructure)

### Local Development Setup

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd pronielts
```

#### 2. Start Local Services

```bash
# Start PostgreSQL and MinIO (Blob Storage mock)
docker-compose up -d

# Verify services are running
docker-compose ps
```

#### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt -r requirements-dev.txt

# Copy environment file
cp .env.example .env

# Generate encryption key
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Add the key to .env as ENCRYPTION_KEY

# Run migrations
alembic upgrade head

# Seed database
psql -h localhost -U pronielts -d pronielts -f ../infrastructure/scripts/seed_database.sql

# Start API
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000
API docs: http://localhost:8000/docs

#### 4. Mobile Setup

```bash
cd mobile

# Get dependencies
flutter pub get

# Generate Hive adapters
flutter packages pub run build_runner build

# Run on simulator/device
flutter run
```

**Note**: Update `apiBaseUrl` in `lib/config/app_config.dart` to your machine's IP for physical device testing.

#### 5. Web Admin Setup

```bash
cd web

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

Web admin will be available at: http://localhost:5173

### Environment Variables

#### Backend (.env)

```bash
PROJECT_NAME="PronIELTS API"
VERSION="1.0.0"
DATABASE_URL="postgresql://pronielts:pronielts@localhost:5432/pronielts"
MOCK_MODE=true
ENCRYPTION_KEY="<generated-fernet-key>"
SECRET_KEY="<random-secret>"
```

#### Mobile (lib/config/app_config.dart)

```dart
static const String apiBaseUrl = 'http://localhost:8000/api/v1';
// For physical device: 'http://<your-ip>:8000/api/v1'
```

#### Web (.env)

```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Development Workflow

### Mock Mode vs Azure Mode

The backend supports two modes:

1. **Mock Mode** (`MOCK_MODE=true`):
   - Speech assessment returns random realistic scores
   - Blob storage saves to local filesystem
   - Perfect for local development without Azure

2. **Azure Mode** (`MOCK_MODE=false`):
   - Uses real Azure Speech SDK
   - Uploads to Azure Blob Storage
   - Requires Azure account and credentials

### Running Tests

#### Backend Tests
```bash
cd backend
pytest --cov=app --cov-report=html
```

#### Mobile Tests
```bash
cd mobile
flutter test --coverage
```

#### Web Tests
```bash
cd web
npm run test
```

## Deployment

### Azure Free Tier Resources

- **Speech Service (F0)**: 5 hours/month free
- **SQL Database (Basic)**: 32GB storage, 5 DTUs
- **App Service (F1)**: 1GB RAM, 60 CPU min/day
- **Blob Storage**: 5GB free
- **Key Vault**: 10,000 operations free
- **Azure AD B2C**: 50,000 MAU free

### Deployment Steps

1. **Create Azure Account**: Follow `docs/azure_setup_guide.md`
2. **Configure Terraform**: Update `infrastructure/terraform/environments/dev.tfvars`
3. **Deploy Infrastructure**: `terraform apply`
4. **Deploy Backend**: Via GitHub Actions or manual
5. **Build Mobile**: `flutter build apk` / `flutter build ios`
6. **Deploy Web Admin**: Azure Static Web Apps

See `docs/deployment_guide.md` for detailed instructions.

## API Documentation

Interactive API documentation is available at `/docs` when running the backend:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Key endpoints:
- `POST /api/v1/assessments/assess` - Submit pronunciation assessment
- `GET /api/v1/dialogs` - List all dialogs
- `GET /api/v1/dialogs/{id}` - Get dialog with phrases
- `GET /api/v1/users/{id}/assessments` - Get user assessment history

See `docs/api_spec.md` for complete API reference.

## Database Schema

```sql
users
  ├── id (PK)
  ├── user_id (anonymous ID)
  ├── email
  ├── full_name
  └── is_active

dialogs
  ├── id (PK)
  ├── title
  ├── category (Professional, Travel, General, Restaurant, IELTS_Part1/2/3)
  ├── description
  └── difficulty_level

phrases
  ├── id (PK)
  ├── dialog_id (FK)
  ├── reference_text
  ├── order
  ├── phonetic_transcription
  └── difficulty

assessments
  ├── id (PK)
  ├── user_id (FK)
  ├── phrase_id (FK)
  ├── accuracy_score
  ├── prosody_score
  ├── fluency_score
  ├── completeness_score
  ├── overall_score
  ├── word_level_scores (JSON)
  ├── recognized_text
  ├── audio_blob_url
  └── created_at
```

See `docs/database_schema.md` for detailed schema documentation.

## Content Categories

The platform includes themed dialogues for different contexts:

1. **Professional**: Tech interviews, workplace scenarios
2. **Travel**: Airport, hotel, directions
3. **General**: Small talk, daily conversation
4. **Restaurant**: Ordering food, making reservations
5. **IELTS Part 1**: Personal information questions
6. **IELTS Part 2**: Long turn (individual speaking)
7. **IELTS Part 3**: Discussion topics

## Security

- ✅ All API endpoints use HTTPS in production
- ✅ Audio files encrypted before blob storage (AES-256)
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ Input validation using Pydantic
- ✅ Secrets managed via Azure Key Vault
- ✅ CORS properly configured
- ✅ Rate limiting on sensitive endpoints
- ✅ JWT token validation for web admin

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

- **Python**: Black + Pylint
- **Dart**: flutter format
- **TypeScript**: ESLint + Prettier

Run formatters before committing:
```bash
# Backend
black backend/app
pylint backend/app

# Mobile
flutter format mobile/lib

# Web
npm run lint --fix
```

## Troubleshooting

### Common Issues

**Backend won't start**:
- Verify PostgreSQL is running: `docker-compose ps`
- Check `.env` file exists and has correct DATABASE_URL
- Run migrations: `alembic upgrade head`

**Mobile app can't connect to API**:
- Use your machine's IP address, not `localhost`
- Check firewall settings
- Verify backend is running: `curl http://localhost:8000/health`

**Audio recording not working**:
- Check microphone permissions
- Test on physical device (simulators have limitations)
- Verify `record` package is properly installed

See [docs/troubleshooting.md](docs/troubleshooting.md) for more solutions.

## Roadmap

### MVP (Current)
- ✅ Basic pronunciation assessment
- ✅ Dialog-based practice
- ✅ Offline support
- ✅ Web admin panel

### Future Enhancements
- 🔮 Real-time feedback during recording
- 🔮 AI-generated personalized exercises
- 🔮 Social features (leaderboards, sharing)
- 🔮 Advanced analytics (progress tracking)
- 🔮 Multiple language support
- 🔮 Native speaker comparisons

## License

[To be determined]

## Support

For questions or issues:
- Open an issue on GitHub
- Email: [your-email]
- Documentation: [docs/](docs/)

## Acknowledgments

- Azure Cognitive Services for Speech SDK
- Flutter community for excellent packages
- FastAPI for the amazing web framework

---

**Built with ❤️ for IELTS learners worldwide**

**Current Status**: 🚧 Under active development (Phase 0 - Foundation)

See [IMPLEMENTATION_TRACKER.md](IMPLEMENTATION_TRACKER.md) for detailed progress.
