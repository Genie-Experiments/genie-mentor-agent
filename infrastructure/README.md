# Genie Mentor Agent Infrastructure

This directory contains the infrastructure configuration for the Genie Mentor Agent platform.

## Local Development

For local development, use the Docker Compose setup:

```bash
docker-compose up
```

This will start all the required services locally, including:
- All microservices
- PostgreSQL database with pgvector extension
- RabbitMQ for messaging
- Frontend application

## Production Deployment

For production deployment, we use a simplified approach:

1. Build the Docker images
2. Push them to a container registry
3. Deploy using the deployment script

```bash
# Build and push images
./deploy.sh build

# Deploy to production
./deploy.sh deploy
```

The deployment script handles the necessary environment configuration and service orchestration for a production environment.
