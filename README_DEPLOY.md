# Deployment Guide

This project is set up for Docker-based deployment to an Ubuntu server (`uac-prod`).

## Prerequisites

1.  **SSH Access**: Ensure you can connect to the server via `ssh ubuntu@uac-prod`.
2.  **Docker & Docker Compose**: Ensure Docker and Docker Compose are installed on the remote server.
3.  **Environment Variables**: You will need your API keys (Google, OpenAlgo).

## Deployment Steps

1.  **Configure your production environment**:
    Ensure you have a `.env.prod` file in your root directory. This file will be copied to the server as `.env`.
    ```bash
    cp .env .env.prod  # Or cp .env.sample .env.prod
    nano .env.prod     # Update with production values
    ```

2.  **Run the deploy script**:
    ```bash
    ./deploy.sh
    ```
    This script will:
    -   Sync the source code to the server.
    -   **Copy `.env.prod` to the server as `.env`.**
    -   Build and start the containers using `docker-compose.prod.yml`.

## Configuration Notes

-   **Environment Variables**: Manage all production secrets in `.env.prod` on your local machine.
-   **MCP Path**: In `.env.prod`, set `MCP_SERVER_PATH=./mcp/mcpserver.py` (since it's relative to the app root in the container).

## Monitoring

To view logs on the server:
```bash
ssh ubuntu@uac-prod "cd ~/trader && docker compose -f docker-compose.prod.yml logs -f"
```

## Troubleshooting

-   **WhatsApp Authentication**: The first time you run the `whatsapp-provider`, you will need to scan the QR code. You can see the QR code in the logs of the `whatsapp-provider` container.
-   **Permissions**: Ensure the `ubuntu` user has permissions to run Docker and `rsync`.
