import os
import sys
from dotenv import load_dotenv

# Ensure root directory is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.whatsapp import whatsapp_agent

load_dotenv()

# Export for ADK discovery
root_agent = whatsapp_agent
root_agent.name = "whatsapp_bot"
root_agent.description = "Direct WhatsApp interaction agent."
