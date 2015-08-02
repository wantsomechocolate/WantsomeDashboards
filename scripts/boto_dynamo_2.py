
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


#table = Table('device_attributes',connection=conn)
tst = Table('timeseriestable',connection=conn)

timeseriesdata=tst.query_2(
    timeseriesname__eq='001EC600229C_2',
    timestamp__between=['2015-07-22','2015-07-29'],
    consistent=True,
    )

##for entry in timeseriesdata:
##    print entry['timeseriesname'], entry['timestamp'], entry['cumulative_electric_usage_kwh']

##data_list=[]
##for entry in timeseriesdata:
##    data_list.append([entry['timeseriesname'],
##                      entry['timestamp'],
##                      entry['cumulative_electric_usage_kwh']]
##                     )
