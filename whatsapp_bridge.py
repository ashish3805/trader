import os
import sys
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
from dotenv import load_dotenv

# Ensure root directory is in path for imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

from tools.whatsapp import wa
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

load_dotenv()

app = FastAPI(title="WhatsApp ADK Bridge")

# 1. Initialize the Session Service
DB_PATH = os.path.join(ROOT_DIR, "trader", "session.db")
session_service = DatabaseSessionService(db_url=f"sqlite+aiosqlite:///{DB_PATH}")

# 2. Global runner placeholder for lazy initialization
_runner = None

async def get_runner():
    global _runner
    if _runner is None:
        from trader.agent import create_root_agent_async
        agent = await create_root_agent_async()
        _runner = Runner(
            agent=agent,
            app_name="trader",
            session_service=session_service
        )
    return _runner

async def process_and_reply(jid: str, text: str):
    """
    Processes the message through the ADK agent and sends the final response to WhatsApp.
    """
    session_id = f"wa_{jid.split('@')[0]}"
    user_id = jid
    target = jid.split('@')[0] if '@s.whatsapp.net' in jid else jid

    print(f"[*] Processing: {text} from {target}")

    try:
        # Session Management
        session = await session_service.get_session(app_name="trader", user_id=user_id, session_id=session_id)
        if not session:
            await session_service.create_session(app_name="trader", user_id=user_id, session_id=session_id)
        
        await asyncio.sleep(0.5)

        new_message = types.Content(role="user", parts=[types.Part(text=text)])
        runner = await get_runner()
        
        final_response = ""
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message
        ):
            # Log Events
            if calls := event.get_function_calls():
                for call in calls:
                    print(f"[🛠️ Tool Call] {call.name}({call.args})")
            
            if resps := event.get_function_responses():
                for resp in resps:
                    r_content = getattr(resp, 'response', str(resp))
                    resp_str = str(r_content)[:100] + "..." if len(str(r_content)) > 100 else str(r_content)
                    print(f"[🔧 Tool Response] {resp.name}: {resp_str}")

            if event.is_final_response():
                if hasattr(event.content, 'parts') and event.content.parts:
                    final_response = event.content.parts[0].text
                else:
                    final_response = str(event.content)
            
            if event.usage_metadata:
                usage = event.usage_metadata
                print(f"[📊 Usage] Total Tokens: {usage.total_token_count}")

        if final_response:
            print(f"[*] Replying to {target}...")
            # Using a custom timeout for wa.send to avoid bridge timeouts
            wa.send(target, final_response)
        else:
            print(f"[!] No response for {target}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[!] Error: {str(e)}")
        try:
            wa.send(target, f"⚠️ Error: {str(e)}")
        except:
            pass

@app.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        payload = await request.json()
        if payload.get("event") == "message":
            msg_data = payload.get("data")
            sender_jid = msg_data.get("from")
            text = msg_data.get("body")
            if sender_jid and text:
                background_tasks.add_task(process_and_reply, sender_jid, text)
                return {"status": "queued"}
    except Exception as e:
        print(f"[!] Webhook error: {str(e)}")
    return {"status": "ignored"}

@app.get("/status")
async def status():
    return {"status": "online"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6000)
