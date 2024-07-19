from aws_cdk import (
    Stack,
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
    aws_dynamodb as dynamodb,
    aws_cognito as cognito
)
from constructs import Construct

class PyRestApiStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Create a DynamoDB table for users
        user_table = dynamodb.Table(self, "UserTable",
            partition_key=dynamodb.Attribute(name="sub", type=dynamodb.AttributeType.STRING)
        )
        
        # Create a Cognito User Pool
        user_pool = cognito.UserPool(self, "UserPool",
            self_sign_up_enabled=True,
            sign_in_aliases=cognito.SignInAliases(username=True, email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True)
        )
        
        user_pool_client = cognito.UserPoolClient(self, "UserPoolClient",
            user_pool=user_pool,
            auth_flows=cognito.AuthFlow(
                admin_user_password=True,
                custom=True,
                user_password=True,
                user_srp=True
            )
        )
        
        # Create a Lambda function for signup
        signup_lambda = lambda_.Function(self, "SignupFunction",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="signup.handler",
            code=lambda_.Code.from_asset("services"),
            environment={
                'USER_POOL_ID': user_pool.user_pool_id,
                'USER_POOL_CLIENT_ID': user_pool_client.user_pool_client_id
            }
        )
        
        # Create a Lambda function for login
        login_lambda = lambda_.Function(self, "LoginFunction",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="login.handler",
            code=lambda_.Code.from_asset("services"),
            environment={
                'USER_POOL_ID': user_pool.user_pool_id,
                'USER_POOL_CLIENT_ID': user_pool_client.user_pool_client_id
            }
        )
        
        # Create a Lambda function for verifying signup
        verify_signup_lambda = lambda_.Function(self, "VerifySignupFunction",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="verify_signup.handler",
            code=lambda_.Code.from_asset("services"),
            environment={
                'USER_POOL_ID': user_pool.user_pool_id,
                'USER_POOL_CLIENT_ID': user_pool_client.user_pool_client_id,
                'USER_TABLE_NAME': user_table.table_name
            }
        )
        
        # Grant the verify signup Lambda function permissions to write to the DynamoDB table
        user_table.grant_write_data(verify_signup_lambda)
        
        # Create a Lambda function for retrieving user info
        get_user_lambda = lambda_.Function(self, "GetUserFunction",
            runtime=lambda_.Runtime.PYTHON_3_8,
            handler="get_user.handler",
            code=lambda_.Code.from_asset("services"),
            environment={
                'USER_TABLE_NAME': user_table.table_name
            }
        )
        
        # Grant the get user Lambda function permissions to read from the DynamoDB table
        user_table.grant_read_data(get_user_lambda)
        
        # Create an API Gateway REST API
        api = apigateway.RestApi(self, "RestApi",
            rest_api_name="ServerlessRestApi"
        )
        
        # Create a Cognito authorizer
        authorizer = apigateway.CognitoUserPoolsAuthorizer(self, "CognitoAuthorizer",
            cognito_user_pools=[user_pool]
        )
        
        # Integrate the signup Lambda function with the API Gateway
        signup_integration = apigateway.LambdaIntegration(signup_lambda)
        
        # Integrate the login Lambda function with the API Gateway
        login_integration = apigateway.LambdaIntegration(login_lambda)
        
        # Integrate the verify signup Lambda function with the API Gateway
        verify_signup_integration = apigateway.LambdaIntegration(verify_signup_lambda)
        
        # Integrate the get user Lambda function with the API Gateway
        get_user_integration = apigateway.LambdaIntegration(get_user_lambda)
        
        # Define the /signup, /login, /verify-signup, and /user resources and methods for the API Gateway
        signup = api.root.add_resource("signup")
        signup.add_method("POST", signup_integration)  # POST /signup
        
        login = api.root.add_resource("login")
        login.add_method("POST", login_integration)  # POST /login
        
        verify_signup = api.root.add_resource("verify-signup")
        verify_signup.add_method("POST", verify_signup_integration)  # POST /verify-signup
        
        user = api.root.add_resource("user")
        user.add_method("GET", get_user_integration, authorization_type=apigateway.AuthorizationType.COGNITO, authorizer=authorizer)  # GET /user
