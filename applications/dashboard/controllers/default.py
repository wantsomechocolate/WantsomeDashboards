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


        ## Fetch Table that keeps acquisuite info
        table = Table('das_attributes',connection=conn)


        ## Must assign value to hash key, in this case it is serial number
        data={
         'serial_number':request.vars['SERIALNUMBER'],
         }



        ## Add the remainder of the data into the table
        ## After the hash key it doesn't matter what they are called
        for key in request.vars:
            print key
            if key!='SERIALNUMBER':
                data[key]=request.vars[key]


        # try:

        table.put_item(data, overwrite=True)

        # except boto.dynamodb2.exceptions.ConditionalCheckFailedException:
        #     table.get_item(serial_number=data['serial_number'])




    ## For right now, this means we are getting data from a device, in the future I will check for the LOGFILE url variable
    elif request.vars['MODE']=='LOGFILEUPLOAD':
        field_storage_object=request.vars['LOGFILE']


        ## If for some reason there isn't actuall a LOGFILE url variable
        if field_storage_object==None:
            return dict(status="FAILURE")

        else:

            ## Save the device information
            ## The device id is going to be the serial_number of parent unit and the modbus address of that unit
            conn=boto.dynamodb2.connect_to_region(
                'us-east-1',
                aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
                aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
                )

            ## Fetch Table that keeps acquisuite info
            table = Table('device_attributes',connection=conn)

            device_id=request.vars['SERIALNUMBER']+'_'+request.vars['MODBUSDEVICE']

            data=dict(device_id=device_id)

            ## Add the remainder of the data into the table
            ## After the hash key it doesn't matter what they are called
            for key in request.vars:
                # print key
                if key!='LOGFILE':
                    data[key]=request.vars[key]

            table.put_item(data, overwrite=True)


            filename_attr=field_storage_object.name
            db.page_visit_data.insert(last_visited=datetime.now(), vars=request.vars, filename=filename_attr, log_file=field_storage_object)


            ## Try to get data out of the file!
            file_data=field_storage_object.file
            file_data_lines=file_data.readlines()


            for line in file_data_lines:
                line_list=line.trim().split(',')
                db.debug_tbl.insert(error_message=line_list)
            
            db.commit()


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