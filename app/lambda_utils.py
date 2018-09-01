import json
import logging

default_content_type = 'application/json'


def get_logger(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    return logger


def create_response(headers=None, body=None, error=None):
    headers = headers or {}
    return {
        'statusCode': '400' if error else '200',
        'body': error.message if error else json.dumps(body),
        'headers': {
            'Content-Type': headers.get('Content-Type', default_content_type),
        },
    }
