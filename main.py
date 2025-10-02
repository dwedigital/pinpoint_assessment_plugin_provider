from fastapi import FastAPI
from helpers import svg_file_to_base64, png_to_base64
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
        "webhookAuthenticationHeader": 'X-Verify',
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
                "description":'Your Base URL for ExampleAssessments. Use `http://localhost:8000` if running local FastAPI server.',
                "placeholder":'http://localhost:8000',
                "required": True,
                "type": "string",
                "useAsHttpHeader": "X_EXAMPLE_BASE_URL",
            },
        ],
    }
    
@app.post("/export")
async def export(assessmentData: dict):
    print ("Received assessment data:", assessmentData)
    # Extract configuration values
    config = assessmentData.get("configuration", {})
    api_key = config.get("apiKey")
    base_url = config.get("apiBaseURL")

    # if api_key != API_KEY:
    #     return {"status": "error", "message": "Invalid API Key"}

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
                "singleSelectOptions": [
                    {"label": "Python Developer", "value": "python_dev"},
                    {"label": "JavaScript Developer", "value": "js_dev"},
                    {"label": "Data Scientist", "value": "data_sci"},
                    ],
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
            {
                "key": "cvDocument",
                "label": "CV",
                "type": "file",
                "required": False,
                "readonly": False,
            },
        ],
        "submitEndpoint": "/create_assessment",
    }

@app.post("/create_assessment")
async def create_assessment(assessmentDetails: dict):
    print("Creating assessment with details:", assessmentDetails)
    # Here you would normally process the assessment creation
    # For this example, we'll just return a success message
    return {
        "status": "success",
        "message": "Assessment created successfully",
        "assessmentId": "12345"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)