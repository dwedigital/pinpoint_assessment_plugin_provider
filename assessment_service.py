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
{"id":1, "name":"Hello World: The Journey Begins"},
{"id":2, "name":"99 Problems But a Syntax Ain't One"},
{"id":3, "name":"Pandas: Not Just Cute Bears"},
{"id":4, "name":"Django Unchained (From PHP)"},
{"id":5, "name":"Teaching Machines to Learn (Instead of Interns)"},
{"id":6, "name":"Deep Learning: It's Not You, It's Gradients"},
{"id":7, "name":"Teaching Computers to Read Between the Lines"},
{"id":8, "name":"DataFrames and Chill"},
{"id":9, "name":"Flask: Because Django Is Too Mainstream"},
{"id":10, "name":"Automating Yourself Out of Boring Tasks"},
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
