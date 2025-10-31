# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (usar npm install porque no hay package-lock.json)
RUN npm install --legacy-peer-deps

# Copy source code
COPY . .

# Build arguments for environment variables (passed from docker-compose)
ARG VITE_API_URL
ARG VITE_TELEGRAM_BOT_NAME
ARG VITE_ADMIN_USER_ID

# Set as environment variables for the build (Vite requires VITE_ prefix)
ENV VITE_API_URL=${VITE_API_URL}
ENV VITE_TELEGRAM_BOT_NAME=${VITE_TELEGRAM_BOT_NAME}
ENV VITE_ADMIN_USER_ID=${VITE_ADMIN_USER_ID}

# Build the app (environment variables are embedded in the bundle)
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
