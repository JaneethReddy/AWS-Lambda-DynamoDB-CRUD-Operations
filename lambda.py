import boto3
import json
from custom_encoder import CustomEncoder
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'Emp_Master'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
empPath = '/emp'
empsPath = '/allemps'
healthPath = '/health'


def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path'] 
    if httpMethod == getMethod and path == empPath:
        response = getEmps()
    elif httpMethod == postMethod and path == empPath:
        response = saveemp(json.loads(event['body']))
    else:
        response = buildResponse((404, 'Not Found'))
    return response



def getEmps():
    try:
        response = table.scan()
        result = response['Items']
        body = {
            'emps': result
        }
        return buildResponse(200, body)
    except:
        logger.exception(
            'Invalid Request')


def saveemp(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)
    except:
        logger.exception(
            'Invalid Request')


def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response
