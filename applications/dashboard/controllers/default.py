# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()







def upload_logfile():

## This script will be for parsing acquisuite data only
## If we get another unit, We add another script!

    from datetime import datetime
    import gzip

    import boto.dynamodb2
    from boto.dynamodb2.table import Table



    ## This means that its sending acquisuite info - not device info
    if request.vars['MODE']=='STATUS':


        ## Connect to Dynamo
        conn=boto.dynamodb2.connect_to_region(
            'us-east-1',
            aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
            aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
            )


        ## Fetch Table that keeps acquisuite info, passing the conn object we just made
        table = Table('das_attributes',connection=conn)


        ## Must assign value to hash key, in this case it is serial number
        data={
         'serial_number':request.vars['SERIALNUMBER'],
         }



        ## Add the remainder of the data into the table
        ## After the hash key it doesn't matter what they are called
        ## Because we already used serial number as the hash key 
        ## We don't need to also have it as an arbitrary name value pair
        for key in request.vars:
            
            if key!='SERIALNUMBER':
                data[key]=request.vars[key]



        ## The exception commented out below would only come up with the overwrite=True were removed from the put_item call
        # try:
        table.put_item(data, overwrite=True)
        # except boto.dynamodb2.exceptions.ConditionalCheckFailedException:
        #     table.get_item(serial_number=data['serial_number'])




    ## This means we are getting data from a device
    elif request.vars['MODE']=='LOGFILEUPLOAD':

        ## Check that there is a logfile in the request
        field_storage_object=request.vars['LOGFILE']


        ## If for some reason there isn't actually a LOGFILE url variable then return failure
        if field_storage_object==None:
            return dict(status="FAILURE")

        ## If there is a log file continue on!
        else:


            ## Create the connection object to talk to dynamo
            conn=boto.dynamodb2.connect_to_region(
                'us-east-1',
                aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
                aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
                )


            ## Fetch Table that keeps device info (passing in our connection object). 
            ## We are going to overwrite the current values for the device
            ## like uptime, parent DAS, etc. 
            table = Table('device_attributes',connection=conn)


            ## Save the device information
            ## The device id is going to be the serial_number of parent unit and the modbus address of that unit
            ## Seperated by an underscore. 
            device_id=request.vars['SERIALNUMBER']+'_'+request.vars['MODBUSDEVICE']


            ## The hash key is the device id! So let's start off the data dictionary (which will go into 
            ## a call to the db later) with it. 
            data=dict(device_id=device_id)


            ## Add the remainder of the data into the table
            ## After the hash key it doesn't matter what they are called
            ## Carefull not to try and store the LOGFILE in the timeseries nosql db.
            ## That would be silly 
            for key in request.vars:
                if key!='LOGFILE':
                    data[key]=request.vars[key]


            ## Again, without overwrite this would throw an exception every time (but the first time)
            ## Will think of a better way to do this at some point. 
            table.put_item(data, overwrite=True)


            ## The file is gzipped(even when they send naturally every 15 minutes)
            ## I can put a check in at some point, but for now its assumed. 
            ## use the native gzip library to read in the gzip file 
            ## which came from the url variable, which web2py turned into a python fieldstorage object
            ## which web2py then put back into the post vars as LOGFILE.
            ## If the mode of r is not passed in (rb in python3), then it will assumed the 
            ## default type which is WRITE (I know right) and it will actually complain that 
            ## you are trying to read from a write-only file :/
            file_handle=gzip.GzipFile(fileobj=field_storage_object.file, mode='r')


            ## This line reads the entire contents of the file into a string. 
            ## I hope they files don't get too big!
            ## I tried using readlines which auto chops up the lines into items of a list
            ## BUT it gives an error, I guess gzip produces a slightly different type of file handle
            ## than the standard python 'open' construct. 
            file_data_as_string=file_handle.read()


            ## If you don't do this, then you will have an empty line at the end of your file and get all the index errors
            file_data_lines=file_data_lines.strip()


            ## The file string comes in with newlines intact, split on the newlines to effectively get rows
            file_data_lines=file_data_as_string.split('\n')

            # db.debug_tbl.insert(error_message=str(file_data_lines))
            # db.commit()
            # db.debug_tbl.insert(error_message=str(file_data_lines[0]))
            # db.commit()
            # db.debug_tbl.insert(error_message=str(file_data_lines[0].split(',')))
            # db.commit()




            ## Connect to the timeseries table, this table has a hash and a range key
            ## The hash key is the timeseries name (which I'm setting to the device ID for now)
            ## and the timestamp (which I'm using the utc string ts straight from the DAS for now)
            ## It is close to ISO format anyway. 
            timeseriestable = Table('timeseriestable',connection=conn)


            ## This with clause is for batch writing. 
            with timeseriestable.batch_write() as batch:


                for row in file_data_lines:

                    ## Get rid of whitespace at the beginning and end of the row
                    # row=row.strip()

                    ## Seperate the 'row' into what would be cells if opened in csv or excel format
                    cells=row.split(',')
                    db.debug_tbl.insert(error_message=str(cells))
                    db.commit()

                    ## for testing purposes get the ts
                    timestamp=cells[0]
                    db.debug_tbl.insert(error_message=str(timestamp))
                    db.commit()

                    ## for testing purposes get the 4th entry (which happens to be the cumulative reading for the kwh)
                    cumulative_reading=cells[4]
                    db.debug_tbl.insert(error_message=str(cumulative_reading))
                    db.commit()


                    ## populate the context manager with our requests
                    ## when the with clause is natrually exited, the batch write request will occur. 
                    batch.put_item(data=dict(
                        timeseriesname=device_id,
                        timestamp=timestamp,
                        cumulative_electric_usage_kwh=cumulative_reading,
                        ))

            
    else:
        return dict(status='MODE value not supported')

    return dict(status="SUCCESS")


# Authenticate
# Check MODE

# If mode is LOGFILEUPLOAD

# check md5sum is same as sent value
# Save or update device information
# Do not use the name supplied by the fieldstorage object, instead supply your own name made up of validated pieces
# Account for the possibility that the name you come up with may exist already

## Loop through the file going a line at a time (one line will be one timestamp)
## Make sure line is <0 but less than 512? why less than 512 byts?
## put the data you want in the locations you want!


#Done!



def view_aws_info():

    import boto.dynamodb2
    from boto.dynamodb2.table import Table
    import os
    from datetime import datetime

    conn=boto.dynamodb2.connect_to_region(
        'us-east-1',
        aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
        aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
        )

    # print conn.list_tables()
    # print request.args[0]

    table = Table(request.args[0],connection=conn)

    all_entries=table.scan()

    return dict(all_entries=all_entries)



## I need a new table for the device info
##


def iframe_test():
    return dict()