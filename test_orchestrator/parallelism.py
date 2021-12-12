import asyncio
from concurrent.futures.process import ProcessPoolExecutor

from typing import Dict
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Job(BaseModel):
    uid: UUID = Field(default_factory=uuid4)
    status: str = "in_progress"
    result: int = None


global_executor = None
jobs: Dict[UUID, Job] = {}


def create_executor():
    global_executor = ProcessPoolExecutor()
    return global_executor


async def run_in_process(fn, *args):
    loop = asyncio.get_event_loop()
    # wait and return result
    return await loop.run_in_executor(global_executor, fn, *args)


# async def start_cpu_bound_task(uid: UUID, param: int) -> None:
#     jobs[uid].result = await run_in_process(cpu_bound_func, param)
#     jobs[uid].status = "complete"


# @app.post("/new_cpu_bound_task/{param}", status_code=HTTPStatus.ACCEPTED)
# async def task_handler(param: int, background_tasks: BackgroundTasks):
#     new_task = Job()
#     jobs[new_task.uid] = new_task
#     background_tasks.add_task(start_cpu_bound_task, new_task.uid, param)
#     return new_task


# @app.get("/status/{uid}")
# async def status_handler(uid: UUID):
#     return jobs[uid]


# @app.on_event("startup")
# async def startup_event():
#     app.state.executor = ProcessPoolExecutor()


# @app.on_event("shutdown")
# async def on_shutdown():
#     app.state.executor.shutdown()
