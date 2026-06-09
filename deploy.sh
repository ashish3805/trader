#!/bin/bash

# Configuration
REMOTE_HOST="uac-prod"
REMOTE_USER="ubuntu"
REMOTE_DIR="/home/ubuntu/trader"

echo "🚀 Starting deployment to ${REMOTE_USER}@${REMOTE_HOST}..."

# 1. Ensure remote directory exists and rsync is installed
echo "🔍 Checking remote environment..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_DIR} && \
    if ! command -v rsync >/dev/null 2>&1; then \
        echo '📦 rsync not found on remote. Attempting to install...'; \
        sudo apt-get update -qy && sudo apt-get install -qy rsync; \
    fi"

# 2. Sync files to remote
echo "📦 Syncing files..."
rsync -avz --delete \
    --exclude '.git/' \
    --exclude '.venv/' \
    --exclude '__pycache__/' \
    --exclude 'node_modules/' \
    --exclude '.idea/' \
    --exclude '.DS_Store' \
    --exclude 'session.db' \
    --exclude '.env*' \
    ./ ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/

# 3. Sync environment configuration
if [ -f .env.prod ]; then
    echo "🔑 Syncing .env.prod to remote..."
    scp .env.prod ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/.env
else
    echo "⚠️  .env.prod not found locally! Skipping env sync."
fi

# 4. Run deployment commands on remote
echo "🛠️ Building and starting containers on remote..."
ssh ${REMOTE_USER}@${REMOTE_HOST} "cd ${REMOTE_DIR} && \
    docker compose -f docker-compose.prod.yml up -d --build"

echo "✅ Deployment complete!"
