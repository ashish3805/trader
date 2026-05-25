# Trader: AI-Native Algorithmic Trading Workspace

`trader` is an advanced algorithmic trading workspace designed for the Indian stock market (NSE/BSE). Built on the **Google Agent Development Kit (ADK)** and the **OpenAlgo** ecosystem, it allows you to build, test, and deploy trading strategies using natural language and AI agents.

## 🚀 Key Features

- **AI-Native Trading**: Interact with the Indian markets using natural language via a Gemini-powered agent.
- **Unified Broker Access**: Powered by **OpenAlgo**, providing a standardized API for 30+ Indian brokers (Angel One, Dhan, Fyers, etc.).
- **Interactive Web UI**: A modern web interface for chatting with your trading assistant, monitoring funds, and managing orders.
- **Fast & Stable**: Uses a local stdio bridge for high-performance tool execution without OAuth complexity.
- **Persistent Sessions**: Powered by SQLite to maintain conversation history and state across CLI and Web UI sessions.

## 🛠️ Project Structure

- `trader/agent.py`: Pure agent definition and tool configuration.
- `.env`: Centralized configuration for API keys and paths.
- `docs/overview.md`: Comprehensive guide on algorithmic trading in India.
- `trader/session.db`: Local SQLite database for persistent chat sessions (git-ignored).

## 🚦 Getting Started

### 1. Prerequisites
- **Python 3.13+** (managed via `uv` recommended).
- **OpenAlgo**: A running instance of OpenAlgo (local or remote).
- **OpenAlgo Bridge**: The `mcpserver.py` script from the OpenAlgo repository.

### 2. Installation
Clone the repository and sync dependencies:
```bash
uv sync
```

### 3. Configuration
Copy the sample environment file and fill in your details:
```bash
cp .env.sample .env
```
Ensure you provide:
- `GOOGLE_API_KEY`: Your Gemini API key.
- `OPENALGO_API_KEY`: Your OpenAlgo API key.
- `MCP_SERVER_PATH`: The absolute path to your `mcpserver.py` file.

### 4. Running the Workspace

#### Option A: Interactive Web UI (Recommended)
Start the visual trading assistant:
```bash
uv run adk web trader --port 8000
```
Then open [http://localhost:8000](http://localhost:8000) in your browser.

#### Option B: Terminal (Quick Chat)
Start a conversation directly in your shell:
```bash
uv run adk run trader
```

## 📖 Further Reading

- [Algo Trading in India Overview](docs/overview.md): Learn about the broker ecosystem, data feeds, and SEBI regulations.
- [OpenAlgo Documentation](https://docs.openalgo.in): Detailed reference for the broker bridge and execution engine.

## 🛡️ Safety & Security
- **API Keys**: Never commit your `.env` or `session.db` files. They are included in `.gitignore` by default.
- **Paper Trading**: We strongly recommend starting in the **OpenAlgo Sandbox** mode before deploying live capital.

---
Built with ❤️ for the AI-Native Trader.
