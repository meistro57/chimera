#!/bin/bash

# Master script to start Chimera dev environment with Docker and open browser
# Handles cleanup on errors

set -e  # Exit on any error

# Cleanup function to shut down containers on failure
cleanup() {
    echo "Error occurred, cleaning up containers..."
    make down 2>/dev/null || true
    exit 1
}

# Set trap to call cleanup on error
trap cleanup ERR INT TERM

echo "Starting Chimera development environment..."

# Start all development services (DB, backend, frontend) with Docker
make dev-db

# Wait for all services to be healthy
echo "Waiting for all services to be ready..."
timeout=60
counter=0
while ! docker compose -f docker-compose.dev.yml ps postgres | grep -q "healthy" && [ $counter -lt $timeout ]; do
    echo "Waiting for PostgreSQL... (${counter}s)"
    sleep 5
    counter=$((counter + 5))
done

if ! docker compose -f docker-compose.dev.yml ps postgres | grep -q "healthy"; then
    echo "PostgreSQL failed to start properly"
    cleanup
fi

# Wait for Redis
timeout=60
counter=0
while ! docker compose -f docker-compose.dev.yml ps redis | grep -q "healthy" && [ $counter -lt $timeout ]; do
    echo "Waiting for Redis... (${counter}s)"
    sleep 5
    counter=$((counter + 5))
done

if ! docker compose -f docker-compose.dev.yml ps redis | grep -q "healthy"; then
    echo "Redis failed to start properly"
    cleanup
fi

# Wait for backend
timeout=60
counter=0
while ! docker compose -f docker-compose.dev.yml ps backend | grep -q "healthy\|running" && [ $counter -lt $timeout ]; do
    echo "Waiting for backend... (${counter}s)"
    sleep 5
    counter=$((counter + 5))
done

if ! docker compose -f docker-compose.dev.yml ps backend | grep -q "healthy\|running"; then
    echo "Backend failed to start properly"
    cleanup
fi

# Wait for frontend to start
timeout=120
counter=0
while ! docker compose -f docker-compose.dev.yml ps frontend | grep -q "running\|healthy" && [ $counter -lt $timeout ]; do
    echo "Waiting for frontend... (${counter}s)"
    sleep 5
    counter=$((counter + 5))
done

if ! docker compose -f docker-compose.dev.yml ps frontend | grep -q "running\|healthy"; then
    echo "Frontend failed to start properly"
    cleanup
fi

echo "All services are ready!"

# Open browser
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open http://localhost:3000
elif command -v open >/dev/null 2>&1; then
    open http://localhost:3000
else
    echo "Please open http://localhost:3000 in your browser"
fi

echo "Chimera dev environment started! Browser opening to http://localhost:3000"
echo ""
echo "Monitoring logs (Ctrl+C to stop all services)..."
echo ""
echo "Useful commands:"
echo "  View logs: make logs"
echo "  Stop all: make down"
echo "  Backend shell: docker exec -it chimera-backend-dev bash"
echo "  Frontend shell: docker exec -it chimera-frontend-dev bash"

# Monitor logs and allow graceful shutdown
trap 'echo ""; echo "Shutting down Chimera services..."; make down; exit 0' INT TERM
make logs