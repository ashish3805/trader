import os
import sys
from dotenv import load_dotenv

# Ensure root directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from google.adk.tools import AgentTool
from mcp import StdioServerParameters

from tools.whatsapp import whatsapp_agent

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
            command=sys.executable,
            args=[MCP_SERVER_PATH, OPENALGO_API_KEY, OPENALGO_HOST]
        )
    )
)

# 3. Create the Root Agent
# This global 'root_agent' is automatically discovered by ADK CLI (adk web/run).
# It can delegate WhatsApp tasks to the whatsapp_agent via AgentTool.
root_agent = Agent(
    model=AGENT_MODEL,
    name='root_agent',
    description='A specialized trading assistant for the Indian stock market.',
    instruction='You are an expert algorithmic trading assistant. Use the OpenAlgo tools for trading and the whatsapp_agent for sending notifications or alerts to the user.',
    tools=[openalgo_mcp_toolset, AgentTool(agent=whatsapp_agent)]
)

