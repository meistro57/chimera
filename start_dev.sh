#!/bin/bash

# Master script to start Chimera dev environment and open browser
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

# Start dev database (blocking)
echo "Starting database services..."
make dev-db

# Wait for database to be healthy
echo "Waiting for database services to be ready..."
timeout=60
counter=0
while ! docker compose -f docker-compose.dev.yml ps postgres | grep -q "healthy\|running" && [ $counter -lt $timeout ]; do
    echo "Waiting for PostgreSQL... (${counter}s)"
    sleep 5
    counter=$((counter + 5))
done

if ! docker compose -f docker-compose.dev.yml ps postgres | grep -q "healthy\|running"; then
    echo "PostgreSQL failed to start properly"
    cleanup
fi

# Wait for Redis to be healthy
counter=0
while ! docker compose -f docker-compose.dev.yml ps redis | grep -q "healthy\|running" && [ $counter -lt $timeout ]; do
    echo "Waiting for Redis... (${counter}s)"
    sleep 5
    counter=$((counter + 5))
done

if ! docker compose -f docker-compose.dev.yml ps redis | grep -q "healthy\|running"; then
    echo "Redis failed to start properly"
    cleanup
fi

echo "Database services are ready!"

# Start backend in background
echo "Starting backend..."
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 5

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "Backend failed to start"
    cleanup
fi

echo "Backend started successfully!"

# Start frontend in background
echo "Starting frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

# Wait a bit for frontend to start
sleep 10

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "Frontend failed to start"
    cleanup
fi

echo "Frontend started successfully!"

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
echo "Monitoring logs (Ctrl+C to stop)..."
echo "PIDs: Backend($BACKEND_PID) Frontend($FRONTEND_PID)"

# Monitor logs and clean up on interrupt
wait_interrupt() {
    trap 'echo "Shutting down services..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; make down; exit 0' INT TERM
    make logs
}

wait_interrupt