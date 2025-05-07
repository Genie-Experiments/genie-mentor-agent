#!/bin/bash

# Simple deployment script for Genie Mentor Agent
# This script handles building, pushing, and deploying the application

set -e

# Configuration
REGISTRY="your-registry.com"  # Replace with your container registry
PROJECT="genie-mentor-bot"
SERVICES=("api-gateway" "bot-service" "memory-service" "data-ingestion-service" "integration-service")
ENV_FILE=".env.production"

# Function to build and push Docker images
build_and_push() {
  echo "Building and pushing Docker images..."
  
  for service in "${SERVICES[@]}"; do
    echo "Building $service..."
    docker build -t "$REGISTRY/$PROJECT/$service:latest" "../services/$service"
    
    echo "Pushing $service..."
    docker push "$REGISTRY/$PROJECT/$service:latest"
  done
  
  echo "Building frontend..."
  docker build -t "$REGISTRY/$PROJECT/frontend:latest" "../frontend"
  
  echo "Pushing frontend..."
  docker push "$REGISTRY/$PROJECT/frontend:latest"
  
  echo "All images built and pushed successfully!"
}

# Function to deploy the application
deploy() {
  echo "Deploying application to production..."
  
  # Load environment variables
  if [ -f "$ENV_FILE" ]; then
    source "$ENV_FILE"
  else
    echo "Warning: Environment file $ENV_FILE not found!"
  fi
  
  # Create a docker-compose.production.yml file
  cat > docker-compose.production.yml <<EOL
version: '3.8'

services:
  api-gateway:
    image: $REGISTRY/$PROJECT/api-gateway:latest
    restart: always
    ports:
      - "${API_GATEWAY_PORT:-8000}:8000"
    environment:
      - BOT_SERVICE_URL=http://bot-service:8001
      - DATA_INGESTION_SERVICE_URL=http://data-ingestion-service:8003
      - INTEGRATION_SERVICE_URL=http://integration-service:8004
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - bot-service
      - memory-service
      - data-ingestion-service
      - integration-service

  bot-service:
    image: $REGISTRY/$PROJECT/bot-service:latest
    restart: always
    environment:
      - MEMORY_SERVICE_URL=http://memory-service:8002
      - DATA_INGESTION_SERVICE_URL=http://data-ingestion-service:8003
      - DATABASE_URL=${DATABASE_URL}
      - LLM_API_KEY=${LLM_API_KEY}
    depends_on:
      - memory-service
      - data-ingestion-service
      - rabbitmq

  memory-service:
    image: $REGISTRY/$PROJECT/memory-service:latest
    restart: always
    environment:
      - DATABASE_URL=${DATABASE_URL}

  data-ingestion-service:
    image: $REGISTRY/$PROJECT/data-ingestion-service:latest
    restart: always
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - MCP_API_KEY=${MCP_API_KEY}

  integration-service:
    image: $REGISTRY/$PROJECT/integration-service:latest
    restart: always
    environment:
      - RABBITMQ_URL=${RABBITMQ_URL}
      - TALENTLMS_API_KEY=${TALENTLMS_API_KEY}
      - SLACK_API_TOKEN=${SLACK_API_TOKEN}

  frontend:
    image: $REGISTRY/$PROJECT/frontend:latest
    restart: always
    ports:
      - "${FRONTEND_PORT:-3000}:3000"
    depends_on:
      - api-gateway

  rabbitmq:
    image: rabbitmq:3-management
    restart: always
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq

volumes:
  rabbitmq-data:
EOL

  # Deploy using docker-compose
  docker-compose -f docker-compose.production.yml up -d
  
  echo "Application deployed successfully!"
}

# Function to display help
show_help() {
  echo "Usage: $0 [command]"
  echo ""
  echo "Commands:"
  echo "  build    Build and push Docker images"
  echo "  deploy   Deploy the application to production"
  echo "  help     Show this help message"
}

# Main script
case "$1" in
  build)
    build_and_push
    ;;
  deploy)
    deploy
    ;;
  help)
    show_help
    ;;
  *)
    echo "Unknown command: $1"
    show_help
    exit 1
    ;;
esac

exit 0
