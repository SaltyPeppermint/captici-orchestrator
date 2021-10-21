import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def read_main():
    return {"msg": "Hello Softwaretechnikpraktikum"}


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("test_orchestrator.main:app",
                host="0.0.0.0", port=8000, reload=True)
