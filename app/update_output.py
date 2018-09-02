import os
import boto3
import json
from urllib.parse import urlparse
from utils import get_logger


logger = get_logger()
s3 = boto3.resource('s3')
ddb = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])


def handler(event, context):
    logger.info(f'Received event: {event}')
    task = json.loads(event['Records'][0]['Sns']['Message'])
    output_uri = urlparse(task['outputUri'])

    bucket_name = output_uri.netloc
    object_key = output_uri.path.lstrip('/')
    message_id = object_key.split('.')[0]

    message = ddb.get_item(Key={'Id': message_id})['Item']
    message['SampleRate'] = task.pop('sampleRate')
    message['VoiceId'] = task.pop('voiceId')
    message['OutputUri'] = task.pop('outputUri')
    message['Status'] = task.pop('taskStatus')
    message['TaskId'] = task.pop('taskId')
    message['Task'] = task
    logger.info(message)
    ddb.put_item(Item=message)

    logger.info(bucket_name)
    logger.info(object_key)
    s3_object = s3.Object(bucket_name, object_key)
    metadata = {
        'SampleRate': message['SampleRate'],
        'VoiceId': message['VoiceId'],
        'TaskId': message['TaskId']
    }
    s3_object.metadata.update(metadata)
    s3_object.copy_from(
        CopySource={'Bucket': bucket_name, 'Key': object_key},
        Metadata=s3_object.metadata,
        MetadataDirective='REPLACE'
    )
