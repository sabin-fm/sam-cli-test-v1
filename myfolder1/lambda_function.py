import http
import boto3
import logging

import json
from custom_encoder import CustomEncoder
from boto3.dynamodb.conditions import Key, Attr
from random import sample

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamoTableName = "assessments"
dynamoDB = boto3.resource('dynamodb')
table = dynamoDB.Table(dynamoTableName)
user_table = dynamoDB.Table("user")

getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'
healthPath = '/health'
assessmentPath = '/assessment'
surveyquestions = '/surveyquestions'
assessmentsPath = '/assessments'


def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200, "All good")
    elif httpMethod == getMethod and path == assessmentPath:
        response = getAssessment(event['queryStringParameters']['id'])
    elif httpMethod == getMethod and path == assessmentsPath:
        response = getAssessments()
    elif httpMethod == getMethod and path == surveyquestions:
        response = getSurveyQuestions(
            event['queryStringParameters']['active'],
            event['queryStringParameters']['validated'],
            event['queryStringParameters']['size'],
            event['queryStringParameters']['category'],
            event['queryStringParameters']['user_id']

        )
    elif httpMethod == postMethod and path == assessmentPath:
        response = saveAssessment(json.loads(event['body']))
    elif httpMethod == patchMethod and path == assessmentPath:
        requestBody = json.loads(event['body'])
        response = modifyAssessment(requestBody['id'], requestBody['updateKey'], requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == assessmentPath:
        requestBody = json.loads(event['body'])
        response = deleteAssessment(requestBody['id'])
    else:
        response = buildResponse(404, 'Not Found')

    return response


def getAssessment(id):
    try:
        response = table.get_item(
            Key={
                'id': id
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'id %s not found' % id})
    except Exception as error:
        logger.exception('Error while getting assessment %s ' % id)
        return buildResponse(500, {'Message': 'Error while getting assessment %s ' % id, 'Error': error})


def getAssessments():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluateKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluateKey'])
        body = {
            'assessments': result
        }
        return buildResponse(200, body)

    except Exception as error:
        logger.exception('Error while getting all assessments')
        return buildResponse(500, {'Message': str(error)})


def resetSurveyQuestionsForUser(user_id):
    try:
        user_table.update_item(
            Key={
                'email': user_id
            },
            UpdateExpression='set #updateKey = :value',
            ExpressionAttributeNames={
                '#updateKey' : "assessment_ids",
            },
            ExpressionAttributeValues={
                ':value': []
            },
            ReturnValues='UPDATED_NEW'
        )
    except Exception as e:
        logger.error("Error while resetting the question for user")
        raise Exception("Error while resetting the question for user")
    
def checkFilterSurveyQuestion(survey_question, assessment_ids):
    if survey_question.get('id') not in assessment_ids:
        return True
    return False




def getSurveyQuestions(active, validated, size, category, user_id):
    try:
        user = user_table.get_item(
            Key={
                'email': user_id
            }
        )
        assessment_query = table.scan(
            FilterExpression=Attr('category').eq(category) &
            Attr('active').eq(bool(active)) & Attr('validated').eq(bool(validated)))
        
        surveyquestions = assessment_query['Items']
        result = []
        user_d = user['Item']
        if user_d.get('assessment_ids') is None:
            assessment_ids = []
        else:
            if category == 'survey':
                assessment_ids = user_d.get('assessment_ids')
                if len(assessment_ids) == len(surveyquestions):
                    resetSurveyQuestionsForUser(user_id)
                    assessment_ids = []
            else:
                assessment_ids = []

        for surveyquestion in surveyquestions:
            if (checkFilterSurveyQuestion(surveyquestion, assessment_ids)
            ):
                result.append(surveyquestion)

        if (int(size) > len(result)):
            size = len(result)
        body = {
            'operation': 'RETRIEVE',
            'Message': 'Success',
            'TotalItems': len(result),
            'GetAttributes': sample(result, int(size))
        }
        return buildResponse(200, body)
        
    except Exception as error:
        logger.exception('Error while getting all assessments')
        return buildResponse(500, {'Message': str(error)})

def saveAssessment(requestBody):
    try:
        response = table.put_item(Item=requestBody)
        body = {
            'operation': 'SAVE',
            'Message': 'Success',
            'assessment': requestBody
        }
        return buildResponse(200, body)
        
    except:
        logger.exception('Error while saving assessment')
        return buildResponse(500, {'Message': 'Error while saving assessment'})

def modifyAssessment(id, updateKey, updateValue):
    try:
        response = table.update_item(
            Key={
                'id': id
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
        logger.exception('Error while updating assessment')
        return buildResponse(500, {'Message': 'Error while updating assessment'})

def deleteAssessment(id):
    try:
        response = table.delete_item(
            Key={
                'id': id
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'operation': 'DELETE',
            'Message': 'Success',
            'deletedassessment': response
        }
        return buildResponse(200, body)
        
    except:
        logger.exception('Error while deleting assessment')
        return buildResponse(500, {'Message': 'Error while deleting assessment'})




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


