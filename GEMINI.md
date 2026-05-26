# Project Instructions: Trader

This project is an AI-native algorithmic trading workspace for the Indian stock market, integrating the **Google Agent Development Kit (ADK)** with **OpenAlgo**.

## Architectural Standards

### 1. Agent Discovery
- The workspace follows the ADK multi-agent directory pattern.
- **Trader Agent**: Defined in `trader/agent.py`.
- **WhatsApp Bot**: Defined in `whatsapp_bot/agent.py`.
- **WhatsApp Automation**:
    - `tools/whatsapp_provider.js`: A custom Node.js listener that forwards incoming WhatsApp messages (including self-messages) to the bridge.
    - `whatsapp_bridge.py`: An automated webhook service that links WhatsApp JIDs to ADK sessions and runs the agent logic.
- Run `adk web .` from the root to discover all agents in the workspace.
- The `root_agent` in `trader/agent.py` can also delegate to the `whatsapp_agent` via `AgentTool`.
- Always use the ADK CLI for execution.

### 2. OpenAlgo Connectivity
- We use the **Local stdio bridge** method for maximum stability.
- The `mcpserver.py` bridge is spawned as a subprocess using `StdioConnectionParams`.
- Remote MCP (OAuth) is **not used** due to rate-limiting and Handshake SSE issues with remote WAFs.
- Configuration is centralized in the root `.env` file (`OPENALGO_API_KEY`, `OPENALGO_HOST`, `MCP_SERVER_PATH`).

### 3. Session Management
- Conversation state is persisted in a local SQLite database: `trader/session.db`.
- This database is shared across CLI and Web UI runs.
- **Security**: `session.db` and `.env` must never be committed to Git.

### 4. Code Style
- **Pure Definitions**: Keep `agent.py` focused purely on definitions. No `if __name__ == "__main__"` or manual runner logic.
- **Configurability**: Key parameters like `AGENT_MODEL` should be read from environment variables.
- **Idiomatic Python**: Follow PEP 8 and use modern type hinting.

## Common Workflows

### Running the Web UI
```bash
uv run adk web trader --port 8000
```

### Running the CLI
```bash
uv run adk run trader
```

### Configuration Template
See `.env.sample` for the required environment variables.

## Project Structure
- `trader/`: Main trading agent definition.
- `whatsapp_bot/`: Standalone WhatsApp interaction agent.
- `whatsapp_provider/`: Node.js WhatsApp connection service (the "Radio").
- `tools/`: Shared tool libraries and sub-agent definitions (e.g., `whatsapp.py`).
- `docs/`: Supplemental documentation and guides.
- `.agents/skills/`: Installed MCP skills for technical analysis.
- `skills-lock.json`: Lock file for MCP skills.
