# Build stage for production or dev setup
FROM node:18-alpine as base

WORKDIR /app

# Copy package files
COPY package.json ./
COPY package-lock.json* ./

# Install dependencies
RUN npm cache clean --force && npm ci

# Copy source code
COPY . .

# Production stage
FROM base as production

# Build the application
RUN npm run build

# Serve with nginx
FROM nginx:alpine
COPY --from=production /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s CMD wget --no-verbose --tries=1 --spider http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]

# Development stage
FROM base as development

# Install curl for health checks
RUN apk add --no-cache curl

EXPOSE 3000

# Health check for dev (check if Vite is listening on port 3000)
HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:3000/ || exit 1

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]