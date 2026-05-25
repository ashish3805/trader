import os
from wabridge import WABridge

# Initialize WABridge
# Default base_url is http://localhost:3000
wa = WABridge()

def send_whatsapp_message(phone: str, message: str) -> dict:
    """
    Sends a WhatsApp message to a specific phone number.
    
    Args:
        phone: The recipient's phone number with country code (e.g., '919876543210').
        message: The text message to send.
    """
    try:
        response = wa.send(phone, message)
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_whatsapp_to_self(message: str) -> dict:
    """
    Sends a WhatsApp message to your own number (the linked account).
    Use it when the recipient number is not known.
    
    Args:
        message: The text message to send.
    """
    try:
        response = wa.send(message)
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_whatsapp_groups() -> dict:
    """
    Retrieves a list of all WhatsApp groups the account is a member of.
    """
    try:
        groups = wa.groups()
        return {"status": "success", "groups": groups}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def send_whatsapp_to_group(group_id: str, message: str) -> dict:
    """
    Sends a WhatsApp message to a specific group.
    
    Args:
        group_id: The WhatsApp group JID (e.g., '120363023456789@g.us').
        message: The text message to send.
    """
    try:
        response = wa.send_group(group_id, message)
        return {"status": "success", "response": response}
    except Exception as e:
        return {"status": "error", "message": str(e)}

from google.adk.agents.llm_agent import Agent

# Define the WhatsApp Agent
whatsapp_agent = Agent(
    model=os.getenv("AGENT_MODEL", "gemini-1.5-flash"),
    name='whatsapp_agent',
    description='A specialized agent for sending WhatsApp notifications and alerts.',
    instruction='You are a WhatsApp communication expert. Use your tools to send messages to individuals, yourself, or groups. When asked to notify the user via WhatsApp, use this agent.',
    tools=[send_whatsapp_message, send_whatsapp_to_self, get_whatsapp_groups, send_whatsapp_to_group]
)
