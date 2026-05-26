# Node.js Provider Dockerfile
FROM node:20-slim

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY whatsapp_provider.js ./

# Default environment variables
ENV PORT=3000
ENV WEBHOOK_URL=http://whatsapp-bridge:6000/webhook
ENV AUTH_DIR=/app/auth

# Create auth directory
RUN mkdir -p /app/auth

EXPOSE 3000

CMD ["node", "whatsapp_provider.js"]
