import unittest
import boto3
from boto3.dynamodb.conditions import Key
import requests
import time


class IntegrationTests(unittest.TestCase):

    def setUp(self):
        cf = boto3.client('cloudformation', region_name='us-east-1')
        stacks = cf.describe_stacks(StackName='say-it-int')
        self.api_endpoint = stacks['Stacks'][0]['Outputs'][0]['OutputValue']
        self.dynamodb = boto3.resource(
            'dynamodb', region_name='us-east-1'
        ).Table('int-say-it-messages')

    def test_execution_flow_happy_path(self):
        request = {
            'Message': 'This is a test message',
            'OutputFormat': 'mp3',
            'SampleRate': '8000'
        }

        response = requests.post(
            url=self.api_endpoint,
            json=request
        )

        self.assertEqual(200, response.status_code)

        record = response.json()
        self.assertEqual(request['Message'], record['Message'])
        self.assertEqual(request['OutputFormat'], record['OutputFormat'])
        self.assertEqual(request['SampleRate'], record['SampleRate'])

        # wait for task to complete
        time.sleep(5)
        record = self.dynamodb.query(
            KeyConditionExpression=Key('Id').eq(record['Id'])
        )['Items'][0]
        # change this to complete
        self.assertEqual('Processing', record['Status'])

        # validate output file
