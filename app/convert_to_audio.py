import boto3
from boto3.dynamodb.conditions import Key
import os
from utils import get_logger


logger = get_logger()
messages = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])
polly = boto3.client('polly')


def handler(event, context):
    logger.info(f'Received event: {event}')

    for record in event['Records']:
        if record['eventName'] != 'INSERT':
            continue

        id = record['dynamodb']['Keys']['Id']['S']
        items = messages.query(
            KeyConditionExpression=Key('Id').eq(id)
        )['Items']

        message = items[0] if items else None

        if not message or message['Status'] != 'QUEUED':
            continue

        response = polly.start_speech_synthesis_task(
            OutputFormat=message['OutputFormat'],
            SampleRate=message['SampleRate'],
            OutputS3KeyPrefix=message['Id'],
            OutputS3BucketName=os.environ['BUCKET_NAME'],
            SnsTopicArn=os.environ['SNS_TOPIC_ARN'],
            Text=message['Message'],
            VoiceId=message['VoiceId']
        )
        logger.info(response)

        message.update(
            Status='PROCESSING',
            TaskId=response['SynthesisTask']['TaskId']
        )
        messages.put_item(Item=message)
        logger.info(message)

        return message
