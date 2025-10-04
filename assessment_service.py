from fastapi import FastAPI, HTTPException, Security, APIRouter, Request
from fastapi.responses import HTMLResponse
from helpers import get_assessment_database, write_assessments_database
from fastapi.security import APIKeyHeader
from datetime import datetime
import uuid
from fastapi.templating import Jinja2Templates
import requests

templates = Jinja2Templates(directory="templates")


api_key_header = APIKeyHeader(name="X_EXAMPLE_ASSESSMENTS_KEY")


async def get_api_key(api_key: str = Security(api_key_header)):
    # Replace with your actual API key validation logic
    VALID_API_KEY = "ABCDEFG123456789"
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


app = FastAPI()

# Create a router for protected routes and prefix them with /api
protected_router = APIRouter(prefix="/api", dependencies=[Security(get_api_key)])

allowed_statuses = [
    "pending",
    "completed",
    "abandoned",
    "failed",
    "cancelled",
    "archived",
    "not_started",
]
assessments = get_assessment_database()

PACKAGES = {
    1: "Hello World: The Journey Begins",
    2: "99 Problems But a Syntax Ain't One",
    3: "Pandas: Not Just Cute Bears",
    4: "Django Unchained (From PHP)",
    5: "Teaching Machines to Learn (Instead of Interns)",
    6: "Deep Learning: It's Not You, It's Gradients",
    7: "Teaching Computers to Read Between the Lines",
    8: "DataFrames and Chill",
    9: "Flask: Because Django Is Too Mainstream",
    10: "Automating Yourself Out of Boring Tasks",
}


@app.get("/hello")
async def read_root():
    return HTMLResponse(content="<h1>Hello, World!</h1>", status_code=200)


@protected_router.get("/packages")
async def read_assessments_list():
    return PACKAGES


@protected_router.post("/assessments/")
async def submit_assessment(assessment_details: dict):
    """Submit a new assessment.
    Args:
        assessment_details (dict): The details of the assessment to submit.
    """

    id = uuid.uuid4()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S %z").strip()

    assessment = {
        "id": assessment_details["id"],
        "name": assessment_details["name"],
        "email": assessment_details["email"],
        "status": "pending",
        # find the package with the id
        "description": PACKAGES[int(assessment_details["packageId"])],
        "webhook_url": assessment_details["webhookUrl"],
        "platform_url": assessment_details["platformUrl"],
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    assessments.append(assessment)
    write_assessments_database(assessments)
    return assessment


@app.get("/assessments/{id}")
async def read_assessment(id: str):
    """Render the assessment update page.
    Args:
        id (str): The ID of the assessment to render."""
    for assessment in assessments:
        if assessment["id"] == id:
            return templates.TemplateResponse(
                "update_assessment.html",
                {
                    "request": {},
                    "assessment_id": id,
                    "status": assessment.get("status"),
                },
            )

    return HTMLResponse(
        content=f"<h1>Assessment ID: {id} not found</h1>", status_code=404
    )


@app.post("/assessments/{id}/update")
async def update_assessment(request: Request, id: str):
    """Process the assessment update form submission.
    Args:
        request (Request): The incoming request object.
        id (str): The ID of the assessment to update."""
    form_data = await request.form()
    print(id)
    status = form_data.get("status")
    for assessment in assessments:
        if assessment["id"] == id:
            assessment["status"] = status
            assessment["score"] = form_data.get("score")
            assessment["updated_at"] = (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S %z").strip()
            )
            write_assessments_database(assessments)

            payload = {
                "id": id,
                "status": form_data.get("status"),
                "score": form_data.get("score"),
                "report_path": f"reports/{assessment['id']}",
            }
            print(payload)

            requests.post(assessment["webhook_url"], json=payload, verify=False)
            return templates.TemplateResponse(
                "update_assessment.html",
                {
                    "request": {},
                    "assessment_id": id,
                    "status": assessment.get("status"),
                },
            )

    return HTMLResponse(
        content=f"<h1>Assessment ID: {id} not found</h1>", status_code=404
    )


@app.get("/assessments/reports/{id}")
async def read_assessment_report(id: str):
    """Render the assessment report page.
    Args:
        id (str): The ID of the assessment to render.
    """
    for assessment in assessments:
        if assessment["id"] == id:
            return templates.TemplateResponse(
                "report.html",
                {
                    "request": {},
                    "assessment_id": id,
                    "status": assessment.get("status"),
                    "score": assessment.get("score"),
                    "candidate_name": assessment.get("name"),
                    "description": assessment.get("description"),
                    "assessment_date": assessment.get("created_at"),
                },
            )
    return HTMLResponse(
        content=f"<h1>Assessment Report ID: {id} not found</h1>", status_code=404
    )

# Include the protected router routes
app.include_router(protected_router)

if __name__ == "__main__":

    import uvicorn

    # if you want hotreload, use the command line: uvicorn provider:app --host 0.0.0.0 --port 8001 --reload
    uvicorn.run(app, host="0.0.0.0", port=8001)
