import json
import boto3
import os

client = boto3.client('cognito-idp')

def handler(event, context):
    body = json.loads(event['body'])
    username = body['username']
    password = body['password']

    try:
        response = client.initiate_auth(
            ClientId=os.environ['USER_POOL_CLIENT_ID'],
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Login successful', 'data': response})
        }
    except client.exceptions.NotAuthorizedException:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid username or password'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }
