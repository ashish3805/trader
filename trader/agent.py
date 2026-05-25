import os
from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters

load_dotenv()

# Agent Configuration
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-3.1-flash-lite")

# OpenAlgo Configuration
OPENALGO_API_KEY = os.getenv("OPENALGO_API_KEY")
OPENALGO_HOST = os.getenv("OPENALGO_HOST", "https://trade.uacinfo.com")
# Path to the local OpenAlgo MCP bridge, now externalized to .env
MCP_SERVER_PATH = os.getenv("MCP_SERVER_PATH")

# 1. Initialize OpenAlgo MCP Toolset using the LOCAL BRIDGE
# This spawns the bridge as a subprocess for fast and stable tool execution.
openalgo_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="python",
            args=[MCP_SERVER_PATH, OPENALGO_API_KEY, OPENALGO_HOST]
        )
    )
)

# 2. Create the Agent
# This global 'root_agent' is automatically discovered by ADK CLI (adk web/run).
root_agent = Agent(
    model=AGENT_MODEL,
    name='root_agent',
    description='A specialized trading assistant for the Indian stock market.',
    instruction='You are an expert algorithmic trading assistant. Use the OpenAlgo tools to help the user with market data, order management, and position tracking.',
    tools=[openalgo_mcp_toolset]
)
