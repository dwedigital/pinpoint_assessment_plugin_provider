from fastapi import FastAPI, Header, Request
from helpers import svg_file_to_base64, png_to_base64, get_field_value
from typing import Annotated
import requests as apiRequests
import uuid
import json

app = FastAPI()

API_KEY = "ABCDEFG123456789"
ASSESSMENT_REPORT_PATH  = "http://localhost:8001/assessments/"


@app.get("/hello")
async def index():
    return {"Message": "Hello, World!"}


@app.post("/")
async def config():
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


@app.post("/export")
async def export(request: Request):
    headers = dict(request.headers)
    api_key = headers.get("x_example_assessments_key")
    print(headers)
    print("API Key: ", headers.get("x_example_assessments_key"))
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
        packages = apiRequests.get(
            "http://localhost:8001/packages",
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
        print(f"Error fetching packages: {str(e)}")

    # Extract candidate information
    # candidate_info = assessmentData.get("candidate", {})
    # first_name = candidate_info.get("firstName", "N/A")
    # last_name = candidate_info.get("lastName", "N/A")
    # email = candidate_info.get("email", "N/A")

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


@app.post("/create_assessment")
async def create_assessment(request: Request):
    print("Create Assessment Called")

    form_data = await request.json()
    print("Form Data Received: ", form_data)
    id = uuid.uuid4()
    api_base_url = request.headers.get("x_example_base_url")

    assessment_payload = {
        "id": str(id),
        "name": f"{get_field_value(form_data, 'firstName')} {get_field_value(form_data, 'lastName')}",
        "email": get_field_value(form_data, "email"),
        "packageId": get_field_value(form_data, "selectedTest"),
        "webhookUrl": form_data.get("webhookUrl"),
        "platformUrl": form_data.get("generatedUuidRedirectUrl"),
    }
    print("Assessment Payload: ", assessment_payload)

    try:
        response = apiRequests.post(
            "http://localhost:8001/assessments/",
            json=assessment_payload,
            headers={"X_EXAMPLE_ASSESSMENTS_KEY": API_KEY},
        )
        print("STATUS:", response.status_code)
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
            print("Assessment created successfully:", assessment)
            return {
                "resultVersion": "1.0.0",
                "key": "createAssessment",
                "success": True,
                "assessmentName": assessment["name"],
                "message": "\n".join(
                    [
                        f"{get_field_value(form_data, 'firstName')} was successfully sent to the example assessment plugin.",
                        f"Last name was {get_field_value(form_data, 'lastName')}.",
                        f"The external ID was {str(assessment['id'])}.",
                    ]
                ),
                "status": assessment["status"],
                "externalIdentifier": str(assessment["id"]),
                "externalRecordUrl": f"{api_base_url}/api/{assessment['id']}",
                "externalLinks": [],
            }
    except Exception as e:
        print(f"Error creating assessment: {str(e)}")
        return {
            "status": "error",
            "message": f"Error creating assessment: {str(e)}",
        }


@app.post("/webhook")
async def process_webhook(request: Request):

    print("Webhook Process Called")
    request = await request.json()
    body = json.loads(request["body"])

    print("Webhook Data Received: ", body)

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
                    {"key": "report", "label": "Report", "url": f"{ASSESSMENT_REPORT_PATH}{body.get("report_path")}"}
                ],
            }
        ],
    }


if __name__ == "__main__":
    import uvicorn

    # if you want hotreload, use the command line: uvicorn provider:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
