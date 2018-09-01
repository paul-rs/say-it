import boto3
import json
import os
import uuid
from time import time
from lambda_utils import get_logger, create_response


logger = get_logger()
time_to_live = int(os.environ.get('DAYS_TO_EXPIRE', 1)) * 60 * 60 * 24
dynamodb = boto3.resource('dynamodb')
messages = dynamodb.Table(os.environ['TABLE_NAME'])


def handler(event, context):
    logger.info(f'Received event: {event}')
    request_body = json.loads(event['body'])

    record_id = str(uuid.uuid4().hex)
    message = request_body["message"]

    # Create tracking record in DynamoDB
    record = {
        'Id': record_id,
        'Message': message,
        'Status': 'Queued',
        'Expiration': int(time()) + time_to_live
    }
    messages.put_item(Item=record)

    return create_response(event.get('headers', {}), record, None)
