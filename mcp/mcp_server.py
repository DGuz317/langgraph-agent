import os
import json
import logging
import asyncio
import requests
import datetime
import pandas as pd
import openmeteo_requests
from fastmcp import FastMCP
from typing import Optional, Dict, Any, List


logger = logging.getLogger(__name__)
logging.basicConfig(format="[%(levelname)s]: %(message)s", level=logging.INFO)

mcp = FastMCP("My MCP Server")




if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    logger.info(f"🚀 MCP server started on port {port}")
    asyncio.run(
        mcp.run_async(
            transport="http",
            host="0.0.0.0",
            port=port,
        )
    )
