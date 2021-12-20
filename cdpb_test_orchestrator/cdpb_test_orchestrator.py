# type: ignore
# temporarily disabling pydantic mypy checking due to bug
# https://github.com/samuelcolvin/pydantic/pull/3175#issuecomment-914897604
import uvicorn
from fastapi import FastAPI

from cdpb_test_orchestrator import api, settings
from cdpb_test_orchestrator.storage.sql.database import init_db

app = FastAPI()

app.include_router(api.config.router)
app.include_router(api.project.router)
app.include_router(api.cdpb_test.router)
app.include_router(api.internal.router)


def start():
    init_db()
    is_debug = settings.is_debug()
    "Launched with `poetry run start` at root level"
    if is_debug:
        uvicorn.run(
            "cdpb_test_orchestrator.cdpb_test_orchestrator:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
        )
    else:
        uvicorn.run(
            "cdpb_test_orchestrator.cdpb_test_orchestrator:app",
            host="0.0.0.0",
            port=8000,
            reload=False,
        )

    return


if __name__ == "__main__":
    start()
