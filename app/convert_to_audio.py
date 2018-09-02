import boto3
import os
from utils import get_logger


logger = get_logger()
ddb = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])
polly = boto3.client('polly')


def handler(event, context):
    logger.info(f'Received event: {event}')

    for record in event['Records']:
        if record['eventName'] != 'INSERT':
            continue

        id = record['dynamodb']['Keys']['id']['S']
        item = ddb.get_item(Key={'id': id})
        logger.info(id)
        logger.info(item)
        message = item.get('Item') if item else None

        if not message or message['taskStatus'] != 'QUEUED':
            continue

        response = polly.start_speech_synthesis_task(
            OutputFormat=message['outputFormat'],
            SampleRate=message['sampleRate'],
            OutputS3KeyPrefix=message['id'],
            OutputS3BucketName=os.environ['BUCKET_NAME'],
            SnsTopicArn=os.environ['SNS_TOPIC_ARN'],
            Text=message['message'],
            VoiceId=message['voiceId']
        )
        logger.info(response)

        message.update(
            taskStatus='PROCESSING',
            taskId=response['SynthesisTask']['TaskId']
        )
        ddb.put_item(Item=message)
        logger.info(message)

        return message
