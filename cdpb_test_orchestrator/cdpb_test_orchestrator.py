# type: ignore
# temporarily disabling pydantic mypy checking due to bug
# https://github.com/samuelcolvin/pydantic/pull/3175#issuecomment-914897604
from fastapi import FastAPI

from cdpb_test_orchestrator import api

app = FastAPI()
app.include_router(api.config.router)
app.include_router(api.project.router)
app.include_router(api.cdpb_test.router)
app.include_router(api.internal.router)
