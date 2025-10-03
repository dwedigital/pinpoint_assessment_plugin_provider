from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.responses import HTMLResponse
from helpers import get_assessment_database, write_assessments_database
from fastapi.security import APIKeyHeader
from datetime import datetime
import uuid


api_key_header = APIKeyHeader(name="X_EXAMPLE_ASSESSMENTS_KEY")


async def get_api_key(api_key: str = Security(api_key_header)):
    # Replace with your actual API key validation logic
    VALID_API_KEY = "ABCDEFG123456789"
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_key


app = FastAPI(dependencies=[Depends(get_api_key)])

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


@app.get("/packages")
async def read_assessments_list():
    return PACKAGES


@app.get("/assessments/{id}")
async def read_assessment(id: str):
    for assessment in assessments:
        if assessment["id"] == id:
            return HTMLResponse(
                content=f"<h1>Assessment ID: {id}</h1><p>{assessment["name"]}</p>",
                status_code=200,
            )
    return HTMLResponse(
        content=f"<h1>Assessment ID: {id} not found</h1>", status_code=404
    )


@app.post("/assessments/")
async def submit_assessment(assessment_details: dict):

    id = uuid.uuid4()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S %z').strip()


    assessment = {
        'id': assessment_details['id'],
        'name': assessment_details['name'],
        'email': assessment_details['email'],
        'status': 'pending',
        # find the package with the id
        'description': PACKAGES[int(assessment_details['packageId'])],
        'webhook_url': assessment_details['webhookUrl'],
        'platform_url': assessment_details['platformUrl'],
        'created_at': timestamp,
        'updated_at': timestamp,
        }

    assessments.append(assessment)
    write_assessments_database(assessments)
    return assessment


if __name__ == "__main__":

    import uvicorn

    # if you want hotreload, use the command line: uvicorn provider:app --host 0.0.0.0 --port 8001 --reload
    uvicorn.run(app, host="0.0.0.0", port=8001)
