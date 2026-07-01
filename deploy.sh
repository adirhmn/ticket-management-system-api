#!/bin/bash
# Enable exit on error
set -e

PROJECT_DIR="/home/ubuntu/ticket-management-system-api"


echo "============================================="
echo " Starting Ticket API Deployment on EC2"
echo "============================================="

# Navigate to project directory
cd "$PROJECT_DIR"

# 1. Pull latest code
echo "--> Pulling latest changes from main branch..."
git fetch --all
git reset --hard origin/main

# 2. Re-create / load local .env variables if present
if [ -f .env ]; then
    echo "--> Loading environment variables..."
    export $(cat .env | grep -v '#' | xargs)
else
    echo "WARNING: .env file is missing. Deployment may fail if required env vars are not set."
fi

# 3. Build and launch Docker Compose services
echo "--> Building and starting Docker containers..."
docker compose -f docker-compose.prod.yml up -d --build


# 4. Ensure migrations are applied to database
echo "--> Running database migrations..."
docker compose exec -T web alembic upgrade head

# 5. Clean up unused Docker resources
echo "--> Cleaning up unused Docker images..."
docker image prune -f

# 6. Show status
echo "--> Showing running containers status..."
docker compose ps

# 7. Check application health
echo "--> Verifying service health..."
sleep 3
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000/health)

if [ "$HEALTH_CHECK" -eq 200 ]; then
    echo "SUCCESS: API is up and running!"
    curl -s http://127.0.0.1:8000/health
    echo ""
else
    echo "ERROR: Health check failed with status code $HEALTH_CHECK"
    echo "Container logs:"
    docker compose logs --tail=50
    exit 1
fi

echo "============================================="
echo " Deployment completed successfully!"
echo "============================================="
