import asyncio
import os
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from dotenv import load_dotenv

load_dotenv()

async def test_mcp():
    MCP_SERVER_PATH = os.getenv("MCP_SERVER_PATH")
    OPENALGO_API_KEY = os.getenv("OPENALGO_API_KEY")
    OPENALGO_HOST = os.getenv("OPENALGO_HOST")
    
    print(f"Testing with:")
    print(f"  MCP_SERVER_PATH: {MCP_SERVER_PATH}")
    print(f"  OPENALGO_HOST: {OPENALGO_HOST}")
    
    toolset = McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command="python3",
                args=[MCP_SERVER_PATH, OPENALGO_API_KEY, OPENALGO_HOST]
            )
        )
    )
    
    try:
        print("Initializing toolset...")
        # In ADK, tools are fetched during initialization
        tools = await toolset.get_tools()
        print(f"Successfully fetched {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp())
