import uvicorn

import test_orchestrator.settings
import test_orchestrator.storage.sql.database


def start(debug):
    "Launched with `poetry run start` at root level"
    uvicorn.run(
        "test_orchestrator.test_orchestrator:app",
        host="0.0.0.0",
        port=8000,
        reload=debug,
    )
    return


if __name__ == "__main__":
    Session = test_orchestrator.storage.sql.database.init_db()
    if test_orchestrator.settings.debug_env:
        start(True)
    else:
        start(False)
