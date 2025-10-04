# Pinpoint Assessment Plugin Example

This project demonstrates a FastAPI-based assessment plugin system with two interconnected services: a provider service and an assessment service.

## Prerequisites

- Python 3.7+
- pip

## Setup

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## Running the Services

Both services need to run simultaneously on different ports.

### Service 1: Provider Service (Port 8000)

```bash
# With hot reload (recommended for development)
uvicorn provider:app --host 0.0.0.0 --port 8000 --reload

# Or run directly
python provider.py
```

### Service 2: Assessment Service (Port 8001)

```bash
# With hot reload (recommended for development)
uvicorn assessment_service:app --host 0.0.0.0 --port 8001 --reload

# Or run directly
python assessment_service.py
```

**Note**: Both services must be running for the full workflow to function correctly.

## Service Architecture

### Provider Service ([provider.py](provider.py))

The provider service acts as the integration point for the assessment plugin system. It handles plugin configuration, form generation, and assessment creation.

**Port**: 8000

#### Main Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/hello` | GET | Health check endpoint |
| `/` | POST | Returns plugin configuration including metadata, actions, and form fields |
| `/export` | POST | Generates dynamic form fields for assessment creation (requires API key validation) |
| `/create_assessment` | POST | Creates a new assessment in the assessment service |
| `/webhook` | POST | Processes webhook callbacks from the assessment service |

#### Configuration

- **API Key**: `ABCDEFG123456789` (hardcoded in [provider.py:10](provider.py#L10))
- **Assessment Service URL**: `http://localhost:8001`

#### Key Features

- **Plugin Configuration**: Returns metadata including logo, actions, and configuration form fields
- **API Key Validation**: Validates API key before showing assessment options
- **Dynamic Forms**: Fetches available assessment packages from the assessment service
- **Assessment Creation**: Submits candidate data to the assessment service
- **Webhook Processing**: Receives and processes status updates from completed assessments

### Assessment Service ([assessment_service.py](assessment_service.py))

The assessment service manages assessment packages, candidate assessments, and provides UI for assessment updates.

**Port**: 8001

#### Main Endpoints

| Endpoint | Method | Protected | Description |
|----------|--------|-----------|-------------|
| `/hello` | GET | No | Health check endpoint |
| `/api/packages` | GET | Yes | Returns list of available assessment packages |
| `/api/assessments/` | POST | Yes | Creates a new assessment record |
| `/assessments/{id}` | GET | No | Displays HTML form to update assessment status |
| `/assessments/{id}/update` | POST | No | Updates assessment status and triggers webhook |
| `/assessments/reports/{id}` | GET | No | Displays assessment report |

#### Configuration

- **API Key**: `ABCDEFG123456789` (required in `X_EXAMPLE_ASSESSMENTS_KEY` header for protected routes)
- **Database**: Uses `helpers.py` functions to read/write assessments to persistent storage

#### Key Features

- **API Key Protection**: Protected routes require valid API key in header
- **Assessment Packages**: 10 pre-configured assessment packages ([assessment_service.py:34-45](assessment_service.py#L34-L45))
- **Assessment Management**: Create, read, and update assessments
- **HTML Templates**: Uses Jinja2 templates for assessment update forms and reports
- **Webhook Notifications**: Sends status updates back to provider service via webhooks

## Workflow

1. **Configuration**: Provider service is configured with API key and base URL
2. **Form Generation**: Provider's `/export` endpoint fetches available packages from assessment service
3. **Assessment Creation**: User submits form → Provider creates assessment → Assessment service stores it
4. **Assessment Update**: User accesses `/assessments/{id}` → Updates status/score → Triggers webhook
5. **Webhook Processing**: Assessment service sends update to provided callback URL (Pinpoint) and Pinpoint passes the recieved payload to `provider.py`'s `/webhook` endpoint
6. **Report Viewing**: Assessment reports available at `/assessments/reports/{id}`

## Authentication

Both services use the same API key: `ABCDEFG123456789`

The provider service expects this in configuration and passes it as `X_EXAMPLE_ASSESSMENTS_KEY` header when calling the assessment service.

## Development Notes

- The assessment service stores data using helper functions (`get_assessment_database()`, `write_assessments_database()`)
- Templates are stored in the `templates/` directory
- Logo assets are referenced in the provider service (`logo.png`, `action-logo.svg`)
- Hot reload is enabled when using the `--reload` flag with uvicorn
- `assessment_database.json` is just a mocked database to hold assessments

## Deactivating Virtual Environment

When finished:

```bash
deactivate
```
