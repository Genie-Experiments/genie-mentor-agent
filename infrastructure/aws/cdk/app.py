#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
from stacks.api_gateway_stack import ApiGatewayStack
from stacks.cognito_stack import CognitoStack
from stacks.database_stack import DatabaseStack

app = App()

# Define environments
env_name = app.node.try_get_context("env") or "dev"
env = Environment(
    account=os.environ.get("CDK_DEFAULT_ACCOUNT", ""),
    region=os.environ.get("CDK_DEFAULT_REGION", "us-east-1")
)

# Create stacks
cognito_stack = CognitoStack(app, f"GenieMentorBot-{env_name}-Cognito", env=env)
api_gateway_stack = ApiGatewayStack(
    app, 
    f"GenieMentorBot-{env_name}-ApiGateway", 
    cognito_user_pool=cognito_stack.user_pool,
    env=env
)
database_stack = DatabaseStack(app, f"GenieMentorBot-{env_name}-Database", env=env)

app.synth()
