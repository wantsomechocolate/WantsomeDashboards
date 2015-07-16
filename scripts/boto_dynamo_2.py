
import boto.dynamodb2
from boto.dynamodb2.table import Table
import os
from datetime import datetime


conn=boto.dynamodb2.connect_to_region(
    'us-east-1',
    aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
    aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
    )

print conn.list_tables()


table = Table('device_attributes',connection=conn)

