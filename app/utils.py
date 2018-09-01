import json
import logging
from config import default_content_type


def get_logger(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)

    return logger


def create_response(headers=None, body=None, error=None, status_code=None):
    headers = headers or {}
    status_code = status_code or '400' if error else '200'
    body = body or {}

    return {
        'statusCode': status_code,
        'body': error if error else json.dumps(body),
        'headers': {
            'Content-Type': headers.get(
                'Content-Type', default_content_type
            ),
        },
    }
