# Genie Mentor Agent - AWS CDK Infrastructure

This directory contains the AWS CDK (Cloud Development Kit) implementation for deploying the Genie Mentor Agent infrastructure to AWS.

## Prerequisites

- Python 3.9+
- AWS CLI configured with appropriate credentials
- AWS CDK installed (`npm install -g aws-cdk`)

## Setup

1. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Bootstrap CDK (first time only):

```bash
cdk bootstrap
```

## Deployment

To deploy the infrastructure:

```bash
# Deploy to development environment
cdk deploy --all --context env=dev

# Deploy to production environment
cdk deploy --all --context env=prod
```

## Stacks

The infrastructure is divided into the following stacks:

1. **CognitoStack** - User authentication and authorization
   - User Pool
   - User Pool Client
   - User Pool Domain

2. **ApiGatewayStack** - API management
   - REST API
   - Cognito Authorizer
   - API resources and methods for services

3. **DatabaseStack** - PostgreSQL database with pgvector extension
   - VPC
   - Security Group
   - Parameter Group
   - RDS Instance

## Useful Commands

* `cdk ls`          List all stacks in the app
* `cdk synth`       Emits the synthesized CloudFormation template
* `cdk diff`        Compare deployed stack with current state
* `cdk docs`        Open CDK documentation

## Customization

You can customize the deployment by modifying the context values in `cdk.json` or by passing them as command-line arguments:

```bash
cdk deploy --all --context env=staging --context domain=staging.geniementorbot.com
```
