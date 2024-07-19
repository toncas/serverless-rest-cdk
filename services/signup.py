import json
import boto3
import os

client = boto3.client('cognito-idp')

def handler(event, context):
    body = json.loads(event['body'])
    username = body['username']
    password = body['password']
    email = body['email']

    try:
        response = client.sign_up(
            ClientId=os.environ['USER_POOL_CLIENT_ID'],
            Username=username,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                }
            ]
        )
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Signup successful', 'data': response})
        }
    except client.exceptions.UsernameExistsException:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'User already exists'})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }
