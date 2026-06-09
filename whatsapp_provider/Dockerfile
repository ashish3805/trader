# --- Build Stage ---
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including those needed for builds if any)
RUN npm install --omit=dev && npm cache clean --force

# --- Runtime Stage ---
FROM node:20-alpine

WORKDIR /app

# Copy only node_modules and package.json from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json

# Copy source code
COPY whatsapp_provider.js ./

# Default environment variables
ENV PORT=3000
ENV WEBHOOK_URL=http://whatsapp-bridge:6000/webhook
ENV AUTH_DIR=/app/auth
ENV NODE_ENV=production

# Create auth directory
RUN mkdir -p /app/auth

EXPOSE 3000

CMD ["node", "whatsapp_provider.js"]
