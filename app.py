from fastapi import FastAPI
from Explorations import main_exploration

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to LogicLurker!"}

@app.post("/know_my_vulnerabilities/")
async def know_my_vulnerabilities(target: str, output: str = None, username: str = None, password: str = None, cookie: str = None, token: str = None):
    """
    Endpoint to check for vulnerabilities in a given target URL.
    """
    # Call the main_exploration function with the provided parameters
    result = main_exploration(target, output, username, password, cookie, token)
    
    return {"result": result}
