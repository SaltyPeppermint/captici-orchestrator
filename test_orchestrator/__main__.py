import uvicorn

import test_orchestrator.storage.sql.database


def start():
    """Launched with `poetry run start` at root level"""
    uvicorn.run("test_orchestrator.test_orchestrator:app",
                host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    Session = test_orchestrator.storage.sql.database.init_db()
    start()
