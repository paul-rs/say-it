import os


# API
default_content_type = 'application/json'

# Polly
supported_formats = {
    'mp3': ['8000', '16000', '22050'],
    'ogg_vorbis': ['8000', '16000', '22050'],
    'pcm': ['8000', '16000']
}
default_format = 'mp3'
language_code = 'en-US'

# DynamoDB
time_to_live = int(os.environ.get('DAYS_TO_EXPIRE', 1)) * 60 * 60 * 24
max_throughput_error = 'ProvisionedThroughputExceededException'
