# Project Overview: Trader

This project is an algorithmic trading workspace specifically designed for the Indian stock market (NSE/BSE). It is built around the **OpenAlgo** ecosystem and utilizes specialized **Model Context Protocol (MCP)** skills to provide advanced technical analysis, real-time data streaming, and trade execution capabilities.

The workspace is designed to be "AI-native," allowing developers and traders to use natural language and AI agents to build, backtest, and deploy trading strategies.

## Core Technologies
- **Python**: Primary language for strategy development and data analysis.
- **OpenAlgo**: A 100% open-source broker bridge and execution engine that standardizes API interactions across 30+ Indian brokers.
- **MCP Skills**: Specialized agent capabilities for:
    - **Technical Indicators**: 100+ Numba-optimized indicators via `openalgo.ta`.
    - **Charting**: Interactive Plotly-based financial charts.
    - **Dashboards**: Web-based analytical dashboards using Streamlit or Dash.
    - **Scanners**: Multi-symbol and multi-indicator stock scanning.
    - **Live Feeds**: Real-time WebSocket data processing.
- **Data & Analytics**: `pandas`, `numpy`, `numba`, `yfinance`, `scipy`.
- **Visualization**: `plotly`, `matplotlib`, `seaborn`, `streamlit`.

## Project Structure
- `main.py`: The entry point for the project (currently a placeholder).
- `.agents/skills/`: Contains the installed MCP skills that power the workspace's specialized trading capabilities.
- `skills-lock.json`: Lock file managing the versions and sources of the installed MCP skills.
- `docs/overview.md`: A comprehensive guide on algorithmic trading in India, covering brokers, data ecosystem, and legal frameworks.
- `GEMINI.md`: (This file) Instructional context for Gemini CLI agents.

## Getting Started

### 1. Environment Setup
The project uses **uv** for high-performance Python package and project management.

#### Installation & Setup
- **Install dependencies**: `uv sync` (creates/updates the `.venv`)
- **Add a new package**: `uv add <package-name>`
- **Run scripts**: `uv run <script.py>`

#### Current Stack
The environment is pre-configured with the OpenAlgo trading stack (defined in `pyproject.toml`).

To activate the environment manually (if needed):
- **macOS/Linux**: `source .venv/bin/activate`
- **Windows**: `.venv\Scripts\activate`

### 2. Configuration
Create a `.env` file in the root directory (do not commit this file):
```env
OPENALGO_API_KEY=your_openalgo_api_key_here
OPENALGO_HOST=http://127.0.0.1:5000
```

### 3. Key Workflows
- **Research**: Use `indicator-expert` to inquire about specific technical indicators or trading patterns.
- **Analysis**: Generate charts or scanners using `indicator-chart` or `indicator-scanner`.
- **Deployment**: Implement strategy logic in `main.py` or new script files, leveraging the `openalgo` library for broker execution.

## Development Conventions
- **Surgical Edits**: Use targeted `replace` calls for code modifications to maintain context efficiency.
- **Safety**: Never log, print, or commit API keys or sensitive credentials.
- **Verification**: After modifying indicators or trading logic, verify correctness using sample data or the OpenAlgo sandbox.
- **Idiomatic Python**: Follow PEP 8 standards and prioritize performance by using Numba-optimized functions from `openalgo.ta` where possible.
