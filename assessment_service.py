from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.responses import HTMLResponse
from helpers import get_assessment_database, write_assessments_database
from fastapi.security import APIKeyHeader


api_key_header = APIKeyHeader(name="X_EXAMPLE_ASSESSMENTS_KEY")

async def get_api_key(api_key: str = Security(api_key_header)):
    # Replace with your actual API key validation logic
    VALID_API_KEY = "ABCDEFG123456789" 
    if api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=401, detail="Invalid API Key"
        )
    return api_key


app = FastAPI(dependencies=[Depends(get_api_key)])

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
    

    assessments.append(assessment)
    write_assessments_database(assessments)
    return assessment



if __name__ == "__main__":
    import uvicorn
    # if you want hotreload, use the command line: uvicorn provider:app --host 0.0.0.0 --port 8001 --reload
    uvicorn.run(app, host="0.0.0.0", port=8001)
