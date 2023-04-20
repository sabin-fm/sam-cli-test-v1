from google.oauth2 import service_account
from googleapiclient.discovery import build

# Set up the necessary credentials using the service account's JSON key and domain-wide delegation
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
SERVICE_ACCOUNT_FILE = 'service_account.json'


import logging
from enum import Enum

import json
from custom_encoder import CustomEncoder

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PATCH = "PATCH"
    DELETE = "DELETE"

class HttpPath(Enum):
    HEALTH_PATH = "/health"
    USER_PATH = "/gmail"


def lambda_handler(event, context):

    print(f'Received event: {event}')
    httpMethod = event['httpMethod']
    path = event['path']
    logger.info("Event : %s" % event)
    logger.info("Context: %s" % context)

    if HttpMethod.GET.value.__eq__(httpMethod) and HttpPath.HEALTH_PATH.value.__eq__(path):
        status, response =  200, "All good"
    elif HttpMethod.GET.value.__eq__(httpMethod) and HttpPath.USER_PATH.value.__eq__(path):
        status, response =  checkGmailSetup(event['queryStringParameters']['user_id'])
    else:
        status, response = 404, 'Path Not Found'

    return buildResponse(status, response)

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


def checkGmailSetup(user_id):
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    credentials = credentials.with_subject(user_id)
    service = build('gmail', 'v1', credentials=credentials)

    # Fetch email messages using the Gmail API
    try:
        results = service.users().messages().list(userId='me').execute()
        messages = results.get('messages', [])
        # for message in messages:
        #     msg = service.users().messages().get(userId='me', id=message['id']).execute()
        #     message={
        #         'id':msg['id'],
        #         'text':msg['snippet'],
        #         'timestamp':msg['internalDate']
        #     }
        return 200, "All good"

    except Exception as e:
        logger.error(e)
        return 500, "Gmail setup not working"



