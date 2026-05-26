import os
import sys
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks
import uvicorn
from dotenv import load_dotenv

# Ensure root directory is in path for imports
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(ROOT_DIR)

from trader.agent import root_agent
from tools.whatsapp import wa
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

load_dotenv()

app = FastAPI(title="WhatsApp ADK Bridge")

# 1. Initialize the Session Service
# We point it to the same session.db used by the Web UI for unified context.
# Using sqlite+aiosqlite for async support required by ADK
DB_PATH = os.path.join(ROOT_DIR, "trader", "session.db")
session_service = DatabaseSessionService(db_url=f"sqlite+aiosqlite:///{DB_PATH}")

# 2. Initialize the Runner
# This will orchestrate the agent execution.
runner = Runner(
    agent=root_agent,
    app_name="trader",
    session_service=session_service
)

async def process_and_reply(jid: str, text: str):
    """
    Processes the message through the ADK agent and sends the final response to WhatsApp.
    """
    # Use the JID as the session_id to maintain per-user context
    session_id = f"wa_{jid.split('@')[0]}"
    user_id = jid

    # Extract plain number for wabridge.send (it prefers 919876543210 format)
    target = jid.split('@')[0] if '@s.whatsapp.net' in jid else jid

    print(f"[*] Processing message from {jid} (Session: {session_id}): {text}")

    try:
        # Check if session exists
        session = await session_service.get_session(
            app_name="trader",
            user_id=user_id,
            session_id=session_id
        )
        
        if session:
            print(f"[*] Found existing session for {jid}")
        else:
            print(f"[*] Creating new session for {jid}...")
            session = await session_service.create_session(
                app_name="trader",
                user_id=user_id,
                session_id=session_id
            )
            print(f"[*] Successfully created session for {jid}")

        # Small delay to ensure DB consistency (async sqlite quirk)
        await asyncio.sleep(0.5)

        # Wrap the text in the expected types.Content format
        new_message = types.Content(
            role="user",
            parts=[types.Part(text=text)]
        )

        final_response = ""
        for event in runner.run(
            user_id=user_id,
            session_id=session_id,
            new_message=new_message
        ):
            if event.is_final_response():
                # Extract text from content parts
                if hasattr(event.content, 'parts') and event.content.parts:
                    final_response = event.content.parts[0].text
                else:
                    final_response = str(event.content)

        if final_response:
            print(f"[*] Sending reply to {target}: {final_response[:50]}...")
            wa.send(target, final_response)
        else:
            print(f"[!] No final response generated for {jid}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[!] Error processing message for {jid}: {str(e)}")
        wa.send(target, f"Sorry, I encountered an error processing your request: {str(e)}")

@app.post("/webhook")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint to receive incoming messages from WABridge.
    """
    try:
        payload = await request.json()
        print(f"[*] Received webhook payload: {payload}")
        
        # Payload format from WABridge: {"event": "message", "data": {...}}
        if payload.get("event") == "message":
            msg_data = payload.get("data")
            
            # Extract sender and text
            sender_jid = msg_data.get("from")
            text = msg_data.get("body")
            
            print(f"[*] Message from: {sender_jid}, Body: {text}")
            
            if sender_jid and text:
                # Process in background to respond to webhook immediately
                background_tasks.add_task(process_and_reply, sender_jid, text)
                return {"status": "queued"}
            else:
                print("[!] Missing sender_jid or text in payload data")
        else:
            print(f"[*] Ignored event type: {payload.get('event')}")
            
    except Exception as e:
        print(f"[!] Error in webhook endpoint: {str(e)}")
            
    return {"status": "ignored"}

@app.get("/status")
async def status():
    return {"status": "online", "agent": root_agent.name}

if __name__ == "__main__":
    # Start the server on port 6000
    uvicorn.run(app, host="0.0.0.0", port=6000)
