from fastapi import FastAPI, Request
from helpers import svg_file_to_base64, png_to_base64, get_field_value
from models import (
    HelloResponse,
    ConfigResponse,
    ExportResponse,
    CreateAssessmentSuccessResponse,
    WebhookResponse,
)
import requests
import uuid
import json
import logging

# Configure logging with timestamps
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# Pydantic models for request typing
class WebhookRequest(BaseModel):
    body: str


app = FastAPI()

API_KEY = "ABCDEFG123456789"
ASSESSMENT_REPORT_PATH = "http://localhost:8001/assessments/"


@app.get("/hello", responses={200: {"model": HelloResponse}})
async def index():
    """Health check endpoint.

    Returns:
        dict: A simple greeting message.
    """
    return {"Message": "Hello, World!"}


@app.post("/", responses={200: {"model": ConfigResponse}})
async def config():
    """Pinpoint plugin configuration endpoint.

    Returns the plugin configuration including version, name, logo, actions,
    webhook settings, and configuration form fields. This endpoint is called
    by Pinpoint to understand how to render the plugin within its application.

    Returns:
        dict: Plugin configuration object containing:
            - version: Plugin version
            - name: Plugin display name
            - logoBase64: Base64 encoded logo
            - actions: Available actions with their metadata
            - webhookProcessEndpoint: Webhook processing endpoint
            - webhookAuthenticationHeader: Authentication header for webhooks
            - configurationFormFields: Configuration fields for the plugin
    """
    return {
        "version": "1.0.0",
        "name": "Sample FastAPI Assessment Service",
        "logoBase64": png_to_base64("logo.png"),
        "actions": [
            {
                "key": "createAssessment",
                "label": "Send to ExampleAssessments",
                "iconSvgBase64": svg_file_to_base64("action-logo.svg"),
                "metaEndpoint": "/export",
                "mappings": [
                    {
                        "key": "firstName",
                        "label": "First Name",
                        "value": "{{candidate_first_name}}",
                    },
                    {
                        "key": "lastName",
                        "label": "Last Name",
                        "value": "{{candidate_last_name}}",
                    },
                ],
            }
        ],
        "webhookProcessEndpoint": "/webhook",
        "webhookAuthenticationHeader": "X-Verify",
        "configurationFormFields": [
            {
                "key": "apiKey",
                "label": "API Key",
                "required": True,
                "type": "string",
                "sensitive": True,
                "useAsHttpHeader": "X_EXAMPLE_ASSESSMENTS_KEY",
            },
            {
                "key": "apiBaseURL",
                "label": "Base URL",
                "description": "Your Base URL for ExampleAssessments. Use `http://localhost:8000` if running local FastAPI server.",
                "placeholder": "http://localhost:8000",
                "required": True,
                "type": "string",
                "useAsHttpHeader": "X_EXAMPLE_BASE_URL",
            },
        ],
    }


@app.post("/export", responses={200: {"model": ExportResponse}})
async def export(request: Request):
    """Export metadata endpoint for the createAssessment action.

    Validates API key from headers and fetches available assessment packages
    from the assessment service. Returns form fields for creating an assessment.

    Args:
        request (Request): The incoming request object containing headers.

    Returns:
        dict: Action metadata containing form fields for creating an assessment,
              including test selection, candidate name, and email fields.
    """
    headers = dict(request.headers)
    api_key = headers.get("x_example_assessments_key")
    logger.info(headers)
    logger.info(f"API Key: {headers.get('x_example_assessments_key')}")
    # Extract configuration values

    if api_key != API_KEY or not api_key:
        return {
            "actionVersion": "1.0.0",
            "key": "createAssessment",
            "label": "Send to ExampleAssessments",
            "description": "Sends a candidate to the internal ExampleAssessments system",
            "formFields": [
                {
                    "key": "apiKeyCallout",
                    "label": "No API Key",
                    "type": "callout",
                    "intent": "danger",
                    "description": "No valid API Key provided in configuration. Please update the configuration with a valid API Key.",
                }
            ],
            "submitEndpoint": "/create_assessment",
        }

    try:
        packages = requests.get(
            "http://localhost:8001/api/packages",
            headers={"X_EXAMPLE_ASSESSMENTS_KEY": api_key},
        )
        if packages.status_code != 200:
            raise Exception(
                f"Failed to fetch packages: {packages.status_code} {packages.text}"
            )
        else:
            packages = packages.json()
            packages = [
                {"label": name, "value": str(id)} for id, name in packages.items()
            ]
    except Exception as e:
        logger.error(f"Error fetching packages: {str(e)}")

    return {
        "actionVersion": "1.0.0",
        "key": "createAssessment",
        "label": "Send to ExampleAssessments",
        "description": "Sends a candidate to the internal ExampleAssessments system",
        "formFields": [
            {
                "key": "selectedTest",
                "label": "Selected Test",
                "placeholder": "Select test...",
                "type": "string",
                "required": True,
                "value": "",
                "singleSelectOptions": packages,
            },
            {
                "key": "firstName",
                "label": "First Name",
                "type": "string",
                "required": True,
                "readonly": False,
                "includeValueInRefetch": True,
            },
            {
                "key": "lastName",
                "label": "Last Name",
                "type": "string",
                "required": True,
                "readonly": False,
            },
            {
                "key": "email",
                "label": "Email",
                "type": "string",
                "required": True,
                "readonly": False,
            },
        ],
        "submitEndpoint": "/create_assessment",
    }


@app.post(
    "/create_assessment", responses={200: {"model": CreateAssessmentSuccessResponse}}
)
async def create_assessment(request: Request):
    logger.info("Create Assessment Called")

    logger.info(f"Form Data Received: {data}")
    id = uuid.uuid4()
    api_base_url = request.headers.get("x_example_base_url")

    assessment_payload = {
        "id": str(id),
        "name": f"{get_field_value(data, 'firstName')} {get_field_value(data, 'lastName')}",
        "email": get_field_value(data, "email"),
        "packageId": get_field_value(data, "selectedTest"),
        "webhookUrl": data.get("webhookUrl"),
        "platformUrl": data.get("generatedUuidRedirectUrl"),
    }
    logger.info(f"Assessment Payload: {assessment_payload}")

    try:
        response = requests.post(
            "http://localhost:8001/api/assessments/",
            json=assessment_payload,
            headers={"X_EXAMPLE_ASSESSMENTS_KEY": API_KEY},
        )
        logger.info(f"STATUS: {response.status_code}")
        if response.status_code != 200:
            return {
                "resultVersion": "1.0.0",
                "key": "createAssessment",
                "success": False,
                "toast": {
                    "error": "API Key was blank. Please check the configuration.",
                },
            }
        else:
            assessment = response.json()
            logger.info(f"Assessment created successfully: {assessment}")
            return {
                "resultVersion": "1.0.0",
                "key": "createAssessment",
                "success": True,
                "assessmentName": assessment["name"],
                "message": "\n".join(
                    [
                        f"{get_field_value(data, 'firstName')} was successfully sent to the example assessment plugin.",
                        f"Last name was {get_field_value(data, 'lastName')}.",
                        f"The external ID was {str(assessment['id'])}.",
                    ]
                ),
                "status": assessment["status"],
                "externalIdentifier": str(assessment["id"]),
                "externalRecordUrl": f"{api_base_url}/api/{assessment['id']}",
                "externalLinks": [],
            }
    except Exception as e:
        logger.error(f"Error creating assessment: {str(e)}")
        return {
            "status": "error",
            "message": f"Error creating assessment: {str(e)}",
        }


@app.post("/webhook", responses={200: {"model": WebhookResponse}})
async def process_webhook(request: Request):

    logger.info("Webhook Process Called")
    body = json.loads(webhook_data.body)

    logger.info(f"Webhook Data Received: {body}")

    # Process the webhook data as needed
    # For example, you might want to update the assessment status based on the webhook event

    return {
        "resultVersion": "1.0.0",
        "success": True,
        "updateAssessments": [
            {
                "externalIdentifier": body.get("id"),
                "status": body.get("status"),
                "score": int(body.get("score")),
                "shouldNotify": True,
                "externalLinks": [
                    {
                        "key": "report",
                        "label": "Report",
                        "url": f"{ASSESSMENT_REPORT_PATH}{body.get("report_path")}",
                    }
                ],
            }
        ],
    }


if __name__ == "__main__":
    import uvicorn

    # if you want hotreload, use the command line: uvicorn provider:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
