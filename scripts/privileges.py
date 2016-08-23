import psycopg2
import sys, os
import urlparse

## Get URI
uri = os.environ['WANTSOMEDASHBOARDS_DATABASE_URL']

## Get username
result = urlparse.urlparse(uri)
username = result.username

## Open connection, start cursor, grant privileges
connection = psycopg2.connect(uri)
cursor = connection.cursor()
cursor.execute("""GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO """+username+""";""")

## Commit changes
connection.commit()
connection.close()
