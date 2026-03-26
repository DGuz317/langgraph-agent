"""Convenience methods to start servers."""
import click
from a2a_mcp.mcp import server

@click.command()
@click.option('--run', 'command', default='mcp-server', help='Command to run')
@click.option('--host','host', default='localhost')
@click.option('--port','port', default=10000)
@click.option('--transport','transport', default='streamable-http')
def main(command, host, port, transport) -> None:
    # TODO: Add other servers, perhaps dynamic port allocation
    if command == 'mcp-server':
        server.serve(host, port, transport)
    else:
        raise ValueError(f'Unknown run option: {command}')

if __name__ == '__main__':
    main()