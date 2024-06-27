import json
import boto3
import os
from uuid import uuid4

table_name = os.environ.get('TABLE_NAME')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(table_name)
headers = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': '*',
}

def handler(event, context):
  method = event['httpMethod']
  body = event['body']

  if method == 'POST':
    item = json.loads(body)
    item['id'] = str(uuid4())
    table.put_item(Item=item)
    return {
      'statusCode': 200,
      'body': json.dumps({'id': item['id']}),
      'headers': headers
    }
    
  
  if method == 'GET':
    empl_id = event['queryStringParameters']['id']

    response = table.get_item(Key={
      'id': empl_id
    })
    if 'Item' in response:
      return {
        'statusCode': 200,
        'body': json.dumps(response['Item']),
        'headers': headers
      }
    else:
      return {
        'statusCode': 404,
        'body': json.dumps('Not Found'),
        'headers': headers
      }
