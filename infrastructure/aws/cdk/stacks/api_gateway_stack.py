from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_cognito as cognito,
    aws_iam as iam,
    CfnOutput,
)
from constructs import Construct


class ApiGatewayStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        cognito_user_pool: cognito.UserPool,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create API Gateway
        self.api = apigateway.RestApi(
            self,
            "ApiGateway",
            rest_api_name=f"{construct_id}",
            description="API Gateway for Genie Mentor Agent",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Api-Key",
                ],
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="v1",
                logging_level=apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                metrics_enabled=True,
            ),
        )

        # Create Cognito Authorizer
        authorizer = apigateway.CognitoUserPoolsAuthorizer(
            self, "CognitoAuthorizer", cognito_user_pools=[cognito_user_pool]
        )

        # Create API resources and methods for Bot Service
        bot_service = self.api.root.add_resource("bot-service")

        # Learning Bot
        learning_bot = bot_service.add_resource("learning-bot")
        learning_bot_interact = learning_bot.add_resource("interact")
        learning_bot_interact.add_method(
            "POST",
            apigateway.MockIntegration(
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": '{"response": "This is a mock response from the Learning Bot"}'
                        },
                    )
                ],
                request_templates={"application/json": '{"statusCode": 200}'},
            ),
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={"application/json": apigateway.Model.EMPTY_MODEL},
                )
            ],
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO,
        )

        # Onboarding Bot
        onboarding_bot = bot_service.add_resource("onboarding-bot")
        onboarding_bot_interact = onboarding_bot.add_resource("interact")
        onboarding_bot_interact.add_method(
            "POST",
            apigateway.MockIntegration(
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": '{"response": "This is a mock response from the Onboarding Bot", "sources": []}'
                        },
                    )
                ],
                request_templates={"application/json": '{"statusCode": 200}'},
            ),
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={"application/json": apigateway.Model.EMPTY_MODEL},
                )
            ],
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO,
        )

        # Create API resources and methods for Memory Service
        memory_service = self.api.root.add_resource("memory-service")

        # Conversation Memory
        conversation = memory_service.add_resource("conversation")
        conversation.add_method(
            "POST",
            apigateway.MockIntegration(
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": '{"status": "success"}'
                        },
                    )
                ],
                request_templates={"application/json": '{"statusCode": 200}'},
            ),
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={"application/json": apigateway.Model.EMPTY_MODEL},
                )
            ],
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO,
        )

        # Create API resources and methods for Data Ingestion Service
        data_service = self.api.root.add_resource("data-ingestion-service")

        # RAG Query
        rag = data_service.add_resource("rag")
        query = rag.add_resource("query")
        query.add_method(
            "POST",
            apigateway.MockIntegration(
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": '{"answer": "This is a mock answer from the RAG system", "sources": []}'
                        },
                    )
                ],
                request_templates={"application/json": '{"statusCode": 200}'},
            ),
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={"application/json": apigateway.Model.EMPTY_MODEL},
                )
            ],
            authorizer=authorizer,
            authorization_type=apigateway.AuthorizationType.COGNITO,
        )

        # Outputs
        CfnOutput(
            self, "ApiGatewayUrl", value=self.api.url, description="API Gateway URL"
        )
