from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
from backend.Explorations.main_exploration import MainExploration
app = FastAPI()

class ScanRequest(BaseModel):
    target: str
    output: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    cookie: Optional[str] = None
    token: Optional[str] = None

@app.get("/")
async def read_root():
    return {"message": "Welcome to LogicLurker!"}

@app.post("/know_my_vulnerabilities/")
async def know_my_vulnerabilities(request: ScanRequest):
    """
    Endpoint to check for vulnerabilities in a given target URL.
    """

    # Call the main_exploration function with the provided parameters
    exp = MainExploration(request.target, request.username, request.password, request.cookie, request.token, request.output)
    result = await exp.run()
    return {"result": result}
