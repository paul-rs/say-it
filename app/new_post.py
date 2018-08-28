import boto3
import json
import os
import uuid
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)


def respond(body=None, error=None):
    return {
        'statusCode': '400' if error else '200',
        'body': error.message if error else json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
        },
    }


def handler(event, context):
    logger.info(f'Received event: {event}')
    request_body = json.loads(event['body'])

    arn_parts = context.invoked_function_arn.split(":")
    region = arn_parts[3]
    account_id = arn_parts[4]
    sns_topic = os.environ.get('SNS_TOPIC')
    topic_arn = f'arn:aws:sns:{region}:{account_id}:{sns_topic}'

    recordId = str(uuid.uuid4().hex)
    text = request_body["text"]

    #Create new record in DynamoDB table
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['TABLE_NAME'])
    record = {
        'id' : recordId,
        'text' : text,
        'status' : 'PROCESSING'
    }
    table.put_item(Item=record)
    
    # Send notification about new post to SNS
    # TODO: don't need this, just trigger from dynamodb stream
    logger.info(f'Publishing message to {topic_arn}')
    client = boto3.client('sns')
    client.publish(
        TopicArn = topic_arn,
        Message = recordId
    )
    
    return respond(record, None)
