import botocore
import boto3
import json
import os
import random
import uuid
from time import time
from utils import get_logger, create_response
from config import (
    time_to_live, supported_formats,
    default_format, language_code,
    max_throughput_error
)


logger = get_logger()
messages = boto3.resource('dynamodb').Table(os.environ['TABLE_NAME'])

polly = boto3.client('polly')
valid_voices = None


def handler(event, context):
    logger.info(f'Received event: {event}')
    headers = event.get('headers', {})
    request_body = json.loads(event['body'])

    record_id = str(uuid.uuid4().hex)
    message = request_body.get('Message')
    output_format = request_body.get('OutputFormat') or default_format
    sample_rate = request_body.get('SampleRate')

    if output_format not in supported_formats:
        return create_response(
            headers, None,
            f"Invalid output format '{output_format}'. \
              Supported formats are: {supported_formats}"
        )

    valid_sample_rates = supported_formats[output_format]
    if not sample_rate and sample_rate not in valid_sample_rates:
        return create_response(
            headers, None,
            f"Invalid SampleRate '{sample_rate}'. \
             Allowed values are {valid_sample_rates}"
        )

    voices = (
        valid_voices or
        polly.describe_voices(LanguageCode=language_code)['Voices']
    )

    voice_id = request_body.get('VoiceId') or random.choice(voices)['Id']
    if voice_id not in [x['Id'] for x in voices]:
        return create_response(
            headers, None,
            f"Invalid VoiceId '{voice_id}' for LanguageCode '{language_code}'"
        )

    # Create tracking record in DynamoDB
    record = {
        'Id': record_id,
        'Status': 'Queued',
        'Message': message,
        'OutputFormat': output_format,
        'SampleRate': sample_rate,
        'VoiceId': voice_id,
        'LanguageCode': language_code,
        'Expiration': int(time()) + time_to_live
    }

    try:
        messages.put_item(Item=record)
    except botocore.exceptions.ClientError as err:
        if err.response['Error']['Code'] == max_throughput_error:
            error_code = 429
            error_message = f"Maximum throughput reached. Please retry later."
        else:
            error_code = 400
            error_message = err.response['Error']

        return create_response(
            headers, None, error_message, error_code
        )

    return create_response(headers, record)
