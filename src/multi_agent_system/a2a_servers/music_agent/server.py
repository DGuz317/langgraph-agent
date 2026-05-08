import click
import uvicorn

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from multi_agent_system.common.agent_card_loader import load_agent_card
from multi_agent_system.a2a_servers.music_agent.executor import (
    MusicAgentExecutor,
)


def create_app():
    request_handler = DefaultRequestHandler(
        agent_executor=MusicAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=load_agent_card("music_agent.json"),
        http_handler=request_handler,
    )

    return server.build()


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=11002)
def main(host: str, port: int) -> None:
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()