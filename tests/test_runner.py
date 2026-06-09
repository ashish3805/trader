import asyncio
import os
import sys
from dotenv import load_dotenv

# Ensure root directory is in path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from trader.agent import create_root_agent_async
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

load_dotenv()

async def test_runner():
    print("Initializing components...")
    agent = await create_root_agent_async()
    session_service = DatabaseSessionService(db_url="sqlite+aiosqlite:///:memory:")
    runner = Runner(agent=agent, app_name="test_app", session_service=session_service)
    
    await session_service.create_session(app_name="test_app", user_id="u1", session_id="s1")
    
    msg = types.Content(role="user", parts=[types.Part(text="What is my fund status?")])

    print("Running agent...")
    try:
        async for event in runner.run_async(user_id="u1", session_id="s1", new_message=msg):
            if event.is_final_response():
                 print(f"Final Response: {event.content}")
            elif event.usage_metadata:
                 print(f"Usage: {event.usage_metadata.total_token_count}")
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_runner())
