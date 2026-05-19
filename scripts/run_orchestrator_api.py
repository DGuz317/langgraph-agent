import click
import uvicorn

from multi_agent_system.orchestrator.server import create_app


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=12000)
def main(host: str, port: int) -> None:
    app = create_app()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
