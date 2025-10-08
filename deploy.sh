#!/bin/bash
# Chimera Deployment Script

echo "Deploying Chimera AI Chat..."

# Build and run in production mode
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up -d

# Wait for services
echo "Waiting for services to be ready..."
sleep 10

# Check health
curl -f http://localhost:80 || echo "Frontend not ready"
curl -f http://localhost:8000/health || echo "Backend not ready"

echo "Deployment complete. Access at http://localhost:80"