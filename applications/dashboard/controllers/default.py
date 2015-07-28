# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

@auth.requires_login()
def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    # response.flash = T("Hello World")
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


        ## Now that the info is in dynamo, put some basic info in the db that web2py talks with more easily
        db.das_config.update_or_insert(das_id=request.vars['SERIALNUMBER'])




    ## This means we are getting data from a device
    elif request.vars['MODE']=='LOGFILEUPLOAD':

        ## Check that there is a logfile in the request
        field_storage_object=request.vars['LOGFILE']


        ## If for some reason there isn't actually a LOGFILE url variable then return failure
        if field_storage_object==None:
            return dict(status="FAILURE")

        ## If there is a log file continue on!
        else:

            ## Save the device information
            ## The device id is going to be the serial_number of parent unit and the modbus address of that unit
            ## Seperated by an underscore. 
            device_id=request.vars['SERIALNUMBER']+'_'+request.vars['MODBUSDEVICE']

            ## The log_filename
            log_filename=field_storage_object.name

            ## First thing is to save the logfile in case a false success is achieved!
            ## logfiles are stored in the log_files table
            ## At this point we already know we have a logfile in the url so.....
            db.log_files.insert(
                device_id=device_id,
                log_filename=log_filename,
                log_file=field_storage_object,
                date_added=datetime.now(),
                )


            ## add device info locally. 
            db.device_config.update_or_insert(device_id=device_id)

            ## Commit changes in case errors happen before db io
            ## This saves the files to an S3 bucket
            db.commit()


            ## If we get passed that part, then we can move on to putting the data in Dynamo

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
            ## If the mode of r is not passed in (rb in python3), then it will assume the 
            ## default type which is WRITE (I know right) and it will actually complain that 
            ## you are trying to read from a write-only file :/
            file_handle=gzip.GzipFile(fileobj=field_storage_object.file, mode='r')


            ## This line reads the entire contents of the file into a string. 
            ## I hope the files don't get too big!
            ## I tried using readlines which auto chops up the lines into items of a list
            ## BUT it gives an error, I guess gzip produces a slightly different type of file handle
            ## than the standard python 'open' construct. 
            file_data_as_string=file_handle.read()


            ## If you don't do this, then you will have an empty line at the end of your file and get all the index errors
            ## I'm actually still getting some index errors with this included. But its likely because there was an error line?
            ## It turned out it was just blank lines
            file_data_as_string=file_data_as_string.strip()


            ## The file string comes in with newlines intact, split on the newlines to effectively get rows
            file_data_lines=file_data_as_string.split('\n')


            ## Connect to the timeseries table, this table has a hash and a range key
            ## The hash key is the timeseries name (which I'm setting to the device ID for now)
            ## and the timestamp (which I'm using the utc string ts straight from the DAS for now)
            ## It is close to ISO format anyway. 
            timeseriestable = Table('timeseriestable',connection=conn)



            ## At this point, we need to know what data we are saving from this particular device. 
            ## Acquisuites do a pretty good job of keeping things in the same order accross lines of devices etc
            ## What I'm going to do is assume that if I can't find a configuration for the particular DEVICE, then I 
            ## will save all parameters related to that device. 
            ## If there is a config file found, it will consist of a flag for include or exlcude and the columns
            ## to include or exclude. 
            ## So where do I keep this config information!
            ## at the device level of course in a table that lists devices (Serialnumber_modbusaddress)
            ## In another field it will list the flag, in a third field it will have the columns
            ## if it fails to interpret what is placed in either field it will save all the information to dynamo

            ## So basically, look for the config info in a table called device_config?

            ## This with clause is for batch writing. 
            with timeseriestable.batch_write() as batch:


                for row in file_data_lines:

                    ## Get rid of whitespace at the beginning and end of the row
                    row=row.strip()

                    ## Seperate the 'row' into what would be cells if opened in csv or excel format
                    cells=row.split(',')

                    ## for testing purposes get the ts
                    ## the second slice is to remove the quotes that the acquisuite sends around the ts
                    timestamp=cells[0][1:-1]

                    try:
                        ## for testing purposes get the 4th entry (which happens to be the cumulative reading for the kwh)
                        cumulative_reading=cells[4]

                        ## populate the context manager with our requests
                        ## when the with clause is natrually exited, the batch write request will occur. 
                        ## This is where I should fill up the other fields by default and have mappings
                        ## to configured names and allow user to "include only" or "exclude"
                        batch.put_item(data=dict(
                            timeseriesname=device_id,
                            timestamp=timestamp,
                            cumulative_electric_usage_kwh=cumulative_reading,
                            ))

                    except IndexError:
                        ## Save the lines that counldn't be added 
                        db.debug_tbl.insert(error_message=str(cells), other_info=str(datetime.now()))

            
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



def view_aws_timeseries():
    import boto.dynamodb2
    from boto.dynamodb2.table import Table
    import os
    from datetime import datetime

    conn=boto.dynamodb2.connect_to_region(
        'us-east-1',
        aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
        aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
        )

    tst = Table('timeseriestable',connection=conn)

    timeseriesname=request.args[0]

    timeseriesdata=tst.query_2(
        timeseriesname__eq=timeseriesname,
        consistent=True,
        )

    timeserieslist=[]
    for entry in timeseriesdata:
        timeserieslist.append([entry['timeseriesname'],
                          entry['timestamp'],
                          entry['cumulative_electric_usage_kwh']]
                         )

    return dict(timeserieslist=timeserieslist)



def iframe_test():
    return dict()



def datatables():
    return dict()


def view_aws_datatables():
    return dict()


def ajax_view_aws_timeseries():
    import boto.dynamodb2
    from boto.dynamodb2.table import Table
    import os, json
    from datetime import datetime

    print request.vars

    conn=boto.dynamodb2.connect_to_region(
        'us-east-1',
        aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
        aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
        )

    tst = Table('timeseriestable',connection=conn)

    timeseriesname=request.args[0]
    # timeseriesname='001EC600229C_250'

    timeseriesdata=tst.query_2(
        timeseriesname__eq=timeseriesname,
        consistent=True,
        )

    timeserieslist=[]
    for entry in timeseriesdata:
        timeserieslist.append([entry['timeseriesname'],
                          entry['timestamp'],
                          entry['cumulative_electric_usage_kwh']]
                         )



    items=int(request.vars['length'])
    start=int(request.vars['start'])
    draw=int(request.vars['draw'])
    end=start+items

    data_dict=dict(
        draw=draw,
        recordsTotal=len(timeserieslist),
        recordsFiltered=len(timeserieslist),
        data=timeserieslist[start:end]
        )

    #return dict(timeserieslist=timeserieslist)
    # print json.dumps(data_dict)
    # return json.dumps(timeserieslist)
    return json.dumps(data_dict)




def ajax_graph_aws_timeseries():
    import boto.dynamodb2
    from boto.dynamodb2.table import Table
    import os, json
    from datetime import datetime

    # print request.vars

    conn=boto.dynamodb2.connect_to_region(
        'us-east-1',
        aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
        aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
        )

    tst = Table('timeseriestable',connection=conn)

    timeseriesname=request.args[0]
    # timeseriesname='001EC600229C_250'

    timeseriesdata=tst.query_2(
        timeseriesname__eq=timeseriesname,
        consistent=True,
        )

    timeserieslist=[]
    datalist=[]
    for entry in timeseriesdata:
        if entry['timestamp'][0]=="'":
            timeserieslist.append([
                        entry['timeseriesname'],
                        entry['timestamp'][1:-1],
                        entry['cumulative_electric_usage_kwh']
                        ])
        else:
           timeserieslist.append([
                        entry['timeseriesname'],
                        entry['timestamp'],
                        entry['cumulative_electric_usage_kwh']
                        ])

        datalist.append(entry['cumulative_electric_usage_kwh'])



    # for i in range(1,len(timeserieslist)):
    #     timeserieslist[i][2]=float(timeserieslist[i][2])-float(timeserieslist[i-1][2])



    # data_dict=dict(data1=timeserieslist)

    # items=int(request.vars['length'])
    # start=int(request.vars['start'])
    # draw=int(request.vars['draw'])
    # end=start+items

    # data_dict=dict(
    #     draw=draw,
    #     recordsTotal=len(timeserieslist),
    #     recordsFiltered=len(timeserieslist),
    #     data=timeserieslist[start:end]
    #     )

    #return dict(timeserieslist=timeserieslist)
    # print json.dumps(data_dict)
    return json.dumps(timeserieslist[-100:])
    # return json.dumps(data_dict)




def d3play():
    return dict()

def device():
    return dict()


def success():
    return dict()


def ajax_dynamo_delete_das():

    das_id=request.args[0]

    return True


def view_table():
    table_name=request.vars['table_name']

    if request.vars['db']=='dynamo':
        return dict(message="Not Supported Yet")

    elif request.vars['db']=='postgres':
        grid=SQLFORM.grid(db[table_name])

        return dict(grid=grid)



# def das_test():
#     das_list=list(db().select(db.das_config.das_id)
#     if '001EC600229C' in das_list:
#         print "yay"
#     return dict(das_list=das_list)