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
        response = getEmp(event['queryStringParameters']['EmpId'])
    elif httpMethod == postMethod and path == empPath:
        response = saveemp(json.loads(event['body']))
    elif httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    else:
        response = buildResponse((404, 'Not Found'))
    return response


def getEmp(EmpId):
    try:
        response = table.get_item(
            Key={
                'EmpId': EmpId
            }
        )
        if EmpId in response:
            return buildResponse(200, response[EmpId])
        else:
            return buildResponse(404, {'Message': 'EmpId: %s not found' % EmpId})
    except:
        logger.exception(
            'Do your custom error handling here. I am just gonna log it out here!!')


def getEmps():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])

        body = {
            'emps': result
        }
        return buildResponse(200, body)
    except:
        logger.exception(
            'Do your custom error handling here. I am just gonna log it out here!!')


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
            'Do your custom error handling here. I am just gonna log it out here!!')



def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response
