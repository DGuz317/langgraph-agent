from typing import Protocol
from pathlib import Path

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, Response

from multi_agent_system.common.observability import configure_observability
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
    configure_observability()
    planner_service = service or PlannerService()
    web_dir = Path(__file__).resolve().parents[1] / "web"
    app = FastAPI(
        title="Multi Agent Planner API",
        version="1.0.0",
    )

    @app.get("/", include_in_schema=False)
    async def chat_app() -> HTMLResponse:
        return HTMLResponse((web_dir / "index.html").read_text(encoding="utf-8"))

    @app.get("/static/{asset_name}", include_in_schema=False)
    async def static_asset(asset_name: str) -> Response:
        media_types = {
            "app.js": "application/javascript",
            "styles.css": "text/css",
        }
        media_type = media_types.get(asset_name)
        if media_type is None:
            return Response(status_code=404)
        return Response(
            (web_dir / asset_name).read_text(encoding="utf-8"),
            media_type=media_type,
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
