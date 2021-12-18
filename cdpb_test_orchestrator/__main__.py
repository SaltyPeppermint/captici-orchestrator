import uvicorn

import cdpb_test_orchestrator.settings
import cdpb_test_orchestrator.storage.sql.database


def start(debug):
    "Launched with `poetry run start` at root level"
    uvicorn.run(
        "cdpb_test_orchestrator.cdpb_test_orchestrator:app",
        host="0.0.0.0",
        port=8000,
        reload=debug,
    )
    return


if __name__ == "__main__":
    Session = cdpb_test_orchestrator.storage.sql.database.init_db()
    if cdpb_test_orchestrator.settings.debug_env:
        start(True)
    else:
        start(False)
