from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from helpers import get_assessment_database, write_assessments_database


app = FastAPI()

assessments = get_assessment_database()

PACKAGES = [
{"id":1, "name":"Python Basics"},
{"id":2, "name":"Advanced Python"},
{"id":3, "name":"Data Science with Python"},
{"id":4, "name":"Web Development with Django"},
{"id":5, "name":"Machine Learning Fundamentals"},
{"id":6, "name":"Deep Learning with TensorFlow"},
{"id":7, "name":"Natural Language Processing"},
{"id":8, "name":"Python for Data Analysis"},
{"id":9, "name":"Flask Web Applications"},
{"id":10, "name":"Python Scripting and Automation"},
]

@app.get("/hello")
async def read_root():
    return HTMLResponse(content="<h1>Hello, World!</h1>", status_code=200)

@app.get("/packages")
async def read_assessments_list():
    print(PACKAGES)
    return PACKAGES

@app.get("/assessments/{id}")
async def read_assessment(id: str):
    for assessment in assessments:
        if assessment["id"] == id:
            return HTMLResponse(content=f"<h1>Assessment ID: {id}</h1><p>{assessment["name"]}</p>", status_code=200)
    return HTMLResponse(content=f"<h1>Assessment ID: {id} not found</h1>", status_code=404)

@app.post("/assessments/")
async def submit_assessment(assessment_details: dict):
    assessment = {
        "id": "1",
        "status": "submitted"
    }

    assessments.append(assessment)
    write_assessments_database(assessments)
    return assessment



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
