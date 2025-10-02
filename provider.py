from fastapi import FastAPI, Header, Request
from helpers import svg_file_to_base64, png_to_base64, get_field_value
from typing import Annotated
import requests as apiRequests

app = FastAPI()

API_KEY = "ABCDEFG123456789"


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
        packages = apiRequests.get("http://localhost:8001/packages", headers={"X_EXAMPLE_ASSESSMENTS_KEY": api_key})
        if packages.status_code != 200:
            raise Exception(f"Failed to fetch packages: {packages.status_code} {packages.text}")
        else:
            packages = packages.json()
            packages =  [{"label": package["name"], "value": str(package["id"])} for package in packages]
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
async def create_assessment(request):
    
    form_data = await request.json()
    print("Form Data Received: ", form_data)

    assessment_payload = {
        "firstName": form_data.get("firstName"),
        "lastName": form_data.get("lastName"),
        "email": form_data.get("email"),
        "packageId": form_data.get("selectedTest"),
    }

    try:
        response = apiRequests.post(
            "http://localhost:8001/assessments/",
            json=assessment_payload,
            headers={"X_EXAMPLE_ASSESSMENTS_KEY": API_KEY},
        )
        if response.status_code != 200:
            raise Exception(f"Failed to create assessment: {response.status_code} {response.text}")
        else:
            assessment = response.json()
            print("Assessment created successfully:", assessment)
            return {
                "status": "success",
                "message": "Assessment created successfully",
                "assessmentId": assessment.get("id"),
                "assessmentLink": f"http://localhost:8001/assessments/{assessment.get('id')}",
            }
    except Exception as e:
        print(f"Error creating assessment: {str(e)}")
        return {
            "status": "error",
            "message": f"Error creating assessment: {str(e)}",
        }

    return


if __name__ == "__main__":
    import uvicorn

    # if you want hotreload, use the command line: uvicorn provider:app --host 0.0.0.0 --port 8000 --reload
    uvicorn.run(app, host="0.0.0.0", port=8000)
