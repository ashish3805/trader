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

def get_openalgo_mcp_toolset():
    """Returns a freshly initialized McpToolset with increased timeout."""
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=["-u", MCP_SERVER_PATH, OPENALGO_API_KEY, OPENALGO_HOST]
            ),
            timeout=30.0  # Increased from default 5.0s for production stability
        )
    )

# 3. Create the Root Agent
# This global 'root_agent' is automatically discovered by ADK CLI.
# The tools include the Toolset directly for robust session management.
root_agent = Agent(
    model=AGENT_MODEL,
    name='root_agent',
    description='A specialized trading assistant for the Indian stock market.',
    instruction='''You are an expert algorithmic trading assistant. 
You have access to OpenAlgo tools for trading (placing orders, checking funds, getting quotes, etc.) and a whatsapp_agent for sending notifications.
Always use the tools provided to get real-time data or perform actions.''',
    tools=[get_openalgo_mcp_toolset(), AgentTool(agent=whatsapp_agent)]
)

# Keep factory function for compatibility with latest bridge refactor
async def create_root_agent_async():
    return root_agent

