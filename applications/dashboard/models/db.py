# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()



import os


###############################################################################################
###############################################################################################
###############################################################################################

if 'WANTSOMEDASHBOARDS_DATABASE_URL' in os.environ:

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

###############################################################################################
###############################################################################################
###############################################################################################





## app configuration made easy. Look inside private/appconfig.ini
from gluon.contrib.appconfig import AppConfig
## once in production, remove reload=True to gain full speed
myconf = AppConfig(reload=True)



if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB

    #db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])


    if 'RUNNING_ON_HEROKU' in os.environ:
        


        uri=os.environ['WANTSOMEDASHBOARDS_DATABASE_URL']
        db = DAL(uri, pool_size=10)




    elif 'RUNNING_ON_BEANSTALK' in os.environ:
        uri = "mysql://%(RDS_USERNAME)s:%(RDS_PASSWORD)s@%(RDS_HOSTNAME)s:%(RDS_PORT)s/%(RDS_DB_NAME)s" % os.environ
        db = DAL(uri, pool_size=10)
    
    ## do whatever you want!
    else:
        # db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int), check_reserved=['all'])

   

        uri=os.environ['WANTSOMEDASHBOARDS_DATABASE_URL']
        db = DAL(uri, pool_size=10)

        

        # uri = "mysql://%(RDS_USERNAME)s:%(RDS_PASSWORD)s@%(RDS_HOSTNAME)s:%(RDS_PORT)s/%(RDS_DB_NAME)s" % os.environ
        # db = DAL(uri, pool_size=10)

    session.connect(request, response, db=db) # sessions in DB!

else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')





##########################################################################
##########################################################################
##########################################################################

# import psycopg2
# import sys, os
# import urlparse

# ## Get URI
# uri = os.environ['WANTSOMEDASHBOARDS_DATABASE_URL']

# ## Get username
# result = urlparse.urlparse(uri)
# username = result.username

# ## Open connection, start cursor, grant privileges
# connection = psycopg2.connect(uri)
# cursor = connection.cursor()
# cursor.execute("""GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO """+username+""";""")

# ## Commit changes
# connection.commit()
# connection.close()


##########################################################################
##########################################################################
##########################################################################





## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Service, PluginManager

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=False, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
