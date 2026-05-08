from langchain_community.utilities import SQLDatabase

from multi_agent_system.config import settings


def get_db() -> SQLDatabase:
    return SQLDatabase.from_uri(settings.sqlite_db)