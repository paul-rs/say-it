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

    message = ddb.get_item(Key={'id': message_id})['Item']
    attributes = [
        'sampleRate',
        'voiceId',
        'outputUri',
        'taskStatus',
        'taskId'
    ]
    message.update({a: task.pop(a) for a in attributes})
    task.pop('outputFormat')
    message['task'] = task
    ddb.put_item(Item=message)

    s3_object = s3.Object(bucket_name, object_key)
    metadata = {a: message[a] for a in ['sampleRate', 'voiceId', 'taskId']}
    s3_object.metadata.update(metadata)
    s3_object.copy_from(
        CopySource={'Bucket': bucket_name, 'Key': object_key},
        Metadata=s3_object.metadata,
        MetadataDirective='REPLACE'
    )
