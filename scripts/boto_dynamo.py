
import boto.dynamodb2
from boto.dynamodb2.table import Table
import os

## Create a connection object to supply later where necessary
conn=boto.dynamodb2.connect_to_region(
    'us-east-1',
    aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
    aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
    )

## Do some stuff with the conn object
conn.list_tables()



## Fetch a table using Table and our connection object from earlier
table = Table('timeseriestable',connection=conn)

## Add some data to the table (still only one at a time though
##table.put_item(data={
##	'timeseriesname':'test_name',
##	'timestamp':'test_time_stamp_5',
##	'name':'value5',
##	})

## Batch writing, yay!
with table.batch_write() as batch:
	for i in range(5):
		batch.put_item(data={
			'timeseriesname':'test_name',
			'timestamp':'test_time_stamp_'+str(i+12),
			'name':'value'+str(i+12),
			})


query_results = table.query_2(timeseriesname__eq='test_name',timestamp__beginswith='test_time_stamp_')

query_results = table.query_2(timeseriesname__eq='test_name',timestamp__gte='test_time_stamp_5')

query_results = table.query_2(timeseriesname__eq='test_name',timestamp__between=['test_time_stamp_16','test_time_stamp_5'])

##gt
##lt
##gte
##lte
##between
##beginswith
##endswith
