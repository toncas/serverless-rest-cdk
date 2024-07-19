import json
import boto3
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USER_TABLE_NAME'])

def handler(event, context):
    # Get the user ID from the Cognito identity
    user_id = event['requestContext']['authorizer']['claims']['sub']

    try:
        response = table.get_item(
            Key={
                'sub': user_id
            }
        )
        if 'Item' in response:
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'])
            }
        else:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'User not found'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Internal server error', 'error': str(e)})
        }
