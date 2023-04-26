import http
import boto3
import logging

import json
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamoTableName = "userModelConstructs"
dynamoDB = boto3.resource('dynamodb')
table = dynamoDB.Table(dynamoTableName)

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
constructPath = '/construct'
constructsPath = '/constructs'


def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200, "All good")
    elif httpMethod == getMethod and path == constructPath:
        response = getConstruct(event['queryStringParameters']['name'])
    elif httpMethod == getMethod and path == constructsPath:
        response = getConstructs()
    elif httpMethod == postMethod and path == constructPath:
        response = saveConstruct(json.loads(event['body']))
    elif httpMethod == patchMethod and path == constructPath:
        requestBody = json.loads(event['body'])
        response = modifyConstruct(requestBody['name'], requestBody['updateKey'], requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == constructPath:
        requestBody = json.loads(event['body'])
        response = deleteConstruct(requestBody['name'])
    else :
        response = buildResponse(404, 'Not Found')

    return response
    
def getConstruct(name):
    try:
        response = table.get_item(
            Key = {
                'name': name
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'name %s not found' %name})
    except Exception as error :
        logger.exception('Error while getting construct %s ' %name)
        return buildResponse(500, {'Message': 'Error while getting construct %s ' %name, 'Error':  error})

def getConstructs():
    try:
        response = table.scan()
        result = response['Items']
        
        while 'LastEvaluateKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluateKey'])
        body = {
            'constructs': result
        }
        return buildResponse(200, body)
        
    except Exception as error:
        logger.exception('Error while getting all constructs')
        return buildResponse(500, {'Message': str(error)})

def saveConstruct(requestBody):
    try:
        response = table.put_item(Item=requestBody)
        body = {
            'operation': 'SAVE',
            'Message': 'Success',
            'construct': requestBody
        }
        return buildResponse(200, body)
        
    except:
        logger.exception('Error while saving construct')
        return buildResponse(500, {'Message': 'Error while saving construct'})

def modifyConstruct(name, updateKey, updateValue):
    try:
        response = table.update_item(
            Key={
                'name': name
            },
            UpdateExpression='set #updateKey = :value',
            ExpressionAttributeNames={
                '#updateKey' : updateKey,
            },
            ExpressionAttributeValues={
                ':value': updateValue
            },
            ReturnValues='UPDATED_NEW'
        )
        body = {
            'operation': 'UPDATE',
            'Message': 'Success',
            'UpdateAttributes': response
        }
        return buildResponse(200, body)
        
    except:
        logger.exception('Error while updating construct')
        return buildResponse(500, {'Message': 'Error while updating construct'})

def deleteConstruct(name):
    try:
        response = table.delete_item(
            Key={
                'name': name
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'operation': 'DELETE',
            'Message': 'Success',
            'deletedconstruct': response
        }
        return buildResponse(200, body)
        
    except:
        logger.exception('Error while deleting construct')
        return buildResponse(500, {'Message': 'Error while deleting construct'})




def buildResponse(statusCode, body=None):
    response = {
        'statusCode' : statusCode,
        'headers' : {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    return response


