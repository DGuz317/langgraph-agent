import click
import uvicorn
from fastapi import FastAPI

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore

from multi_agent_system.common.agent_card_loader import load_agent_card
from multi_agent_system.a2a_servers.music_agent.executor import MusicAgentExecutor


def create_app() -> FastAPI:
    app = FastAPI(
        title="Music A2A Service",
        version="1.0.0",
    )

    agent_card = load_agent_card("music_agent.json")

    request_handler = DefaultRequestHandler(
        agent_executor=MusicAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    for route in create_agent_card_routes(agent_card):
        app.router.routes.append(route)

    for route in create_jsonrpc_routes(
        request_handler,
        rpc_url="/a2a/jsonrpc/",
    ):
        app.router.routes.append(route)

    return app


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=11002)
def main(host: str, port: int) -> None:
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()