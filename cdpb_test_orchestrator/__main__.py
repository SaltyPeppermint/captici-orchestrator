import uvicorn

import cdpb_test_orchestrator.settings
from cdpb_test_orchestrator.storage.sql.database import init_db


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
    init_db()
    start(cdpb_test_orchestrator.settings.is_debug())
