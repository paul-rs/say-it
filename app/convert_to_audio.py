import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime
import os
import random
from lambda_utils import get_logger


logger = get_logger()
dynamodb = boto3.resource('dynamodb')
messages = dynamodb.Table(os.environ['TABLE_NAME'])
polly = boto3.client('polly')
all_voices = None


def handler(event, context):
    logger.info(f'Received event: {event}')
    voices = (
        all_voices or
        polly.describe_voices(LanguageCode='en-US')['Voices']
    )

    for record in event['Records']:
        if record['eventName'] != 'INSERT':
            continue

        id = record['dynamodb']['Keys']['Id']['S']
        items = messages.query(
            KeyConditionExpression=Key('Id').eq(id)
        )['Items']

        message = items[0] if items else None

        if not message:
            continue

        response = polly.start_speech_synthesis_task(
            OutputFormat='mp3',
            OutputS3BucketName=os.environ.get('BUCKET_NAME'),
            Text=message['Message'],
            VoiceId=random.choice(voices)['Id']
        )
        logger.info(response)

        task = {
            k: str(v) if isinstance(v, datetime) else v
            for k, v in response.get('SynthesisTask', {}).items()
        }

        message.update(Task=task)
        message['Status'] = 'Processing'
        messages.put_item(Item=message)
        logger.info(message)

        return message
