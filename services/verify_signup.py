import json
import boto3
import os

client = boto3.client('cognito-idp')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USER_TABLE_NAME'])

def handler(event, context):
    body = json.loads(event['body'])
    username = body['username']
    confirmation_code = body['confirmation_code']
    first_name = body['first_name']
    last_name = body['last_name']

    try:
        # Confirm the sign up
        response = client.confirm_sign_up(
            ClientId=os.environ['USER_POOL_CLIENT_ID'],
            Username=username,
            ConfirmationCode=confirmation_code
        )

        # Retrieve the user's Cognito user ID (sub)
        user = client.admin_get_user(
            UserPoolId=os.environ['USER_POOL_ID'],
            Username=username
        )
        user_sub = next(attr['Value'] for attr in user['UserAttributes'] if attr['Name'] == 'sub')

        # Add user record to DynamoDB
        table.put_item(
            Item={
                'sub': user_sub,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'email_verified': True
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Signup verification successful'})
        }
    except client.exceptions.UserNotFoundException:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'User not found'})
        }
    except client.exceptions.CodeMismatchException:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid confirmation code'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }
