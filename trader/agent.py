import os
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

# OpenAlgo Configuration
OPENALGO_API_KEY = os.getenv("OPENALGO_API_KEY", "your_openalgo_api_key_here")
OPENALGO_HOST = os.getenv("OPENALGO_HOST", "https://trade.uacinfo.com")

# Path to the local OpenAlgo MCP bridge
# This bridge handles the translation between MCP and the OpenAlgo REST API using the API key.
MCP_SERVER_PATH = "/Users/ashish/algotrade/openalgo/mcp/mcpserver.py"

# Initialize OpenAlgo MCP Toolset using the local bridge
# We use StdioServerParameters to spawn the bridge as a subprocess.
openalgo_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[MCP_SERVER_PATH, OPENALGO_API_KEY, OPENALGO_HOST]
        )
    )
)

root_agent = Agent(
    model='gemini-3.1-flash-lite',
    name='root_agent',
    description='A specialized trading assistant powered by OpenAlgo for the Indian stock market.',
    instruction='You are an expert algorithmic trading assistant. Use the OpenAlgo tools to help the user with market data, order management, and position tracking. Always verify symbols and exchange codes before placing orders.',
    tools=[openalgo_mcp_toolset]
)
