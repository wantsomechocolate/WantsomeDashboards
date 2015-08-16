import boto
import io
import gzip
import os
import csv

import boto.dynamodb2
from boto.dynamodb2.table import Table



conn=boto.s3.connect_to_region(
    'us-east-1',
    aws_access_key_id=os.environ['AWS_WSDS3_KEY'],
    aws_secret_access_key=os.environ['AWS_WSDS3_SECRET']
    )

bucket=conn.get_bucket('wantsomedashboards')

log_file_name='log_files.log_file.800bed7f7f8c2857.6d622d3235302e35354231463331455f332e6c6f672e677a.gz'

key=bucket.get_key('logfiles/'+log_file_name)

fh = gzip.GzipFile(fileobj=io.BytesIO(key.read()))
