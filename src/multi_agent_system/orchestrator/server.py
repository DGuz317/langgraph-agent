from typing import Protocol

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder

from multi_agent_system.orchestrator.schemas import (
    PlannerInvokeRequest,
    PlannerServiceResponse,
)
from multi_agent_system.orchestrator.service import PlannerService

# TODO: With this, can me create an chatbot interface ? With upload database function the mcp will handle the query stuff
class PlannerServiceProtocol(Protocol):
    async def invoke(
        self,
        user_input: str,
        *,
        thread_id: str | None = None,
        resume: bool | None = None,
    ) -> PlannerServiceResponse:
        ...


def create_app(service: PlannerServiceProtocol | None = None) -> FastAPI:
    planner_service = service or PlannerService()
    app = FastAPI(
        title="Multi Agent Planner API",
        version="1.0.0",
    )

    @app.post("/planner/invoke", response_model=PlannerServiceResponse)
    async def invoke_planner(request: PlannerInvokeRequest) -> PlannerServiceResponse:
        response = await planner_service.invoke(
            request.user_input,
            thread_id=request.thread_id,
            resume=request.resume,
        )
        return _json_safe_response(response)

    return app


def _json_safe_response(response: PlannerServiceResponse) -> PlannerServiceResponse:
    raw_result = jsonable_encoder(response.raw_result)

    if not isinstance(raw_result, dict):
        raw_result = {}

    return response.model_copy(
        update={
            "raw_result": raw_result,
        }
    )
