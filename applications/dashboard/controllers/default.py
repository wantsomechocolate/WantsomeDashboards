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
    import io


    import boto.dynamodb2
    from boto.dynamodb2.table import Table



    ## This means that its sending acquisuite info - not device info
    if request.vars['MODE']=='STATUS':

        time=datetime.now()

        print "["+str(time)+"] "+"Recieved a mode of "+ str(request.vars['MODE'])

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
        db.das_config.update_or_insert(
            db.das_config.das_id==request.vars['SERIALNUMBER'],
            das_id=request.vars['SERIALNUMBER'],
            serial_number=request.vars['SERIALNUMBER'],
            last_modified=datetime.now(),
            )

        print "["+str(time)+"] "+"Successfully updated data for "+ str(request.vars['SERIALNUMBER'])

        return dict(status="SUCCESS")


    ## This means we are getting data from a device
    elif request.vars['MODE']=='LOGFILEUPLOAD':

        time=datetime.now()

        print "["+str(time)+"] "+"Recieved a mode of "+ str(request.vars['MODE'])

        print "["+str(time)+"] "+"Logfile upload started!"

        ## Check that there is a logfile in the request
        field_storage_object=request.vars['LOGFILE']


        ## If for some reason there isn't actually a LOGFILE url variable then return failure
        if field_storage_object==None:

            print "["+str(time)+"] "+"No logfile found"

            return dict(status="FAILURE")

        ## If there is a log file continue on!
        else:

            ## Save the device information
            ## The device id is going to be the serial_number of parent unit and the modbus address of that unit
            ## Seperated by an underscore. 
            device_id=request.vars['SERIALNUMBER']+'_'+request.vars['MODBUSDEVICE']

            print "["+str(time)+"] "+"["+str(device_id)+"] "+ "Device ID found"


            ## The log_filename
            log_filename=field_storage_object.name

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"The filename is: "+str(log_filename)+". As always."

            ## First thing is to save the logfile in case a false success is achieved!
            ## logfiles are stored in the log_files table
            ## At this point we already know we have a logfile in the url so.....
            ## This will save duplicate log files :/
            db.log_files.insert(
                device_id=device_id,
                log_filename=log_filename,
                log_file=field_storage_object,
                date_added=datetime.now(),
                )

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Logfile saved!"

            ## add device info locally. 
            db.device_config.update_or_insert(
                db.device_config.device_id==device_id,
                device_id=device_id,
                das_id=request.vars['SERIALNUMBER'],
                last_modified=datetime.now(),
                )

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Device info updated!"

            ## Commit changes in case errors happen before db io
            ## This saves the files to an S3 bucket
            db.commit()








            ## If we get passed that part, then we can move on to putting the data in Dynamo

            ## Create the connection object to talk to dynamo
            conn=boto.dynamodb2.connect_to_region(
                'us-east-1',
                aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
                aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET'],
                )

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Created connection object"

            ## Fetch Table that keeps device info (passing in our connection object). 
            ## We are going to overwrite the current values for the device
            ## like uptime, parent DAS, etc. 
            table = Table('device_attributes',connection=conn)

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Connected to device attributes table"

            ## The hash key is the device id! So let's start off the data dictionary (which will go into 
            ## a call to the db later) with it. 
            data=dict(device_id=device_id)

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Started data dict for device attributes table"

            ## Add the remainder of the data into the table
            ## After the hash key it doesn't matter what they are called
            ## Carefull not to try and store the LOGFILE in the timeseries nosql db.
            ## That would be silly 
            for key in request.vars:
                if key!='LOGFILE':
                    data[key]=request.vars[key]

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Now printing the current state of the data dict for device attributes\n"+str(data)

            ## Again, without overwrite this would throw an exception every time (but the first time)
            ## Will think of a better way to do this at some point. 
            table.put_item(data, overwrite=True)

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Just updated the device attributes table in aws"



            ## now we are ready to deal with the actual data 

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Beginning the process of saving the interval data"

            try:
                ## Now get what fields you want to collect

                ## This says - look in db table device config for a device with id device_id, then from the records that match (should be 1), 
                ## only select the field device_field_groups. Take the first record (again, should only be one) and give me just the value
                ## without the dot operator at the end it would be a dictionary
                device_field_group = db(db.device_config.device_id==device_id).select(db.device_config.device_field_groups).first().device_field_groups

                print "["+str(time)+"] "+"["+str(device_id)+"] "+"Device field group: " + str(device_field_group)

                ## So we have the name of the group
                ## Now we can get the fields that we want to collect
                device_fields_collect = db(db.device_field_groups.field_group_name==device_field_group).select().first().field_group_columns

                print "["+str(time)+"] "+"["+str(device_id)+"] "+"Device fields collect:" + str(device_fields_collect)

            ## If for some reason there are not fields to get, or getting the fields causes an error
            ## set the variable to ALL
            except:

                print "["+str(time)+"] "+"["+str(device_id)+"] "+"There was a problem, using ALL instead"

                device_fields_collect='ALL'

            if device_fields_collect==None:

                print "["+str(time)+"] "+"["+str(device_id)+"] "+"There was a problem, using ALL instead"

                device_fields_collect='ALL'





            ## The file is gzipped(even when they send naturally every 15 minutes)
            ## I can put a check in at some point, but for now its assumed. 
            ## use the native gzip library to read in the gzip file 
            ## which came from the url variable, which web2py turned into a python fieldstorage object
            ## which web2py then put back into the post vars as LOGFILE.
            ## So I get the "value" of the field storage object which apparently gives me a string of bytes.
            ## I give that to io.BytesIO because I saw it on this thread (thanks unutbu)
            ## http://stackoverflow.com/questions/4204604/how-can-i-create-a-gzipfile-instance-from-the-file-like-object-that-urllib-url
            ## io.BytesIO apparently gives a file or something as "in memory bytes" whatever the difference between that and a reg file
            ## then I let the gzip library have the file object because it is after all gzipped. 
            ## If the fileobj argument isn't right, it won't always throw an error, but it will not behave like
            ## a regular file object. A lot of trial and error and a crap ton of googling for this line. 
            file_handle=gzip.GzipFile(fileobj=io.BytesIO(field_storage_object.value), mode='r')

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Just created the file handle"


            ## Readlines turns the file into a list of lines in the file
            ## for some reason I think it leaves the last newline in the last list item or something
            ## Don't quote me on that though. 
            lines=file_handle.readlines()


            ## If for some reason there are no lines in the file, then report a failure,
            ## depending on the way you get the file, sometimes you can read through the file before
            ## calling readlines, with will return nothing because the seek will be at the end of the file already. 
            if len(lines)==0:
                print "["+str(time)+"] "+"["+str(device_id)+"] "+"Lines is length 0, aborting"
                return dict(status="FAILURE")

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Just made the lines list"

            ## Connect to the timeseries table, this table has a hash and a range key
            ## The hash key is the timeseries name (which I'm setting to the device ID for now)
            ## and the timestamp (which I'm using the utc string ts straight from the DAS for now)
            ## It is close to ISO format anyway. 
            timeseriestable = Table('timeseriestable',connection=conn)

            print "["+str(time)+"] "+"["+str(device_id)+"] "+"Connected to time series table using same connection object"



            ## Begin the batch writing process, we'll hold off on picking or columns for another bit. 
            print "["+str(time)+"] "+"["+str(device_id)+"] "+"About to enter the with loop for batch writing"

            ## This with clause is for batch writing. 
            with timeseriestable.batch_write() as batch:

                print "["+str(time)+"] "+"["+str(device_id)+"] "+"Inside the with clause"

                for line in lines:

                    ## Get rid of whitespace at the beginning and end of the row
                    line=line.strip()

                    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Line:\n"+str(line)

                    ## Seperate the 'row' into what would be cells if opened in csv or excel format
                    cells=line.split(',')

                    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Cells:\n"+str(cells)

                    ## for testing purposes get the ts
                    ## the second slice is to remove the quotes that the acquisuite sends around the ts
                    timestamp=cells[0][1:-1]

                    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Timestamp:\n"+timestamp

                    ## Start of the data dictionary with the timeseriesname and the timestamp
                    data=dict(
                        timeseriesname=device_id,
                        timestamp=timestamp,
                        )


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

                    if device_fields_collect=='ALL':
                        for index in range(len(cells)):
                            data[device_id+'__'+str(index)]=cells[int(index)]

                    else:
                        for index in device_fields_collect:
                            if index<0:
                                index = len(cells)+index
                            data[device_id+'__'+str(index)]=cells[int(index)]

                    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Data dict for timeseries table:\n"+str(data)


                    batch.put_item(data)



        print "["+str(time)+"] "+"["+str(device_id)+"] "+"Finished adding stuff to timeseries table for this device"

        return dict(status="SUCCESS")


    elif request.vars['MODE']=='CONFIGFILEMANIFEST':

        time=datetime.now()

        ## I believe this is for configuring the aquisuite if you want or something
        ## it basically just sends the same info (actually a couple of fewer peices of info) as the STATUS mode. 
        ## I just print to the logs that it got here and return success. 

        print "["+str(time)+"] "+"Recieved a MODE of "+ str(request.vars['MODE'])+"\n"

        for key in request.vars:
            print "["+str(time)+"] "+str(key)+"\n"+str(request.vars[key])+"\n"

        return dict(status="SUCCESS")

    ## If the mode is not supported
    else:

        time=datetime.now()

        print "["+str(time)+"] "+"Recieved a MODE of "+ str(request.vars['MODE']) + ". This MODE is not supported"

        return dict(status='MODE value not supported')




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



def parse_logfile_from_db():

    import boto
    import io
    import gzip
    import os
    import csv

    import boto.dynamodb2
    from boto.dynamodb2.table import Table

    ## Connection object with our keys
    ## These come from the environment which is supplied by the hosting service (heroku, beanstalk), or by the local environment
    ## via .bashrc. Google setting environment variables in python or something for your os. 
    conn=boto.s3.connect_to_region(
        'us-east-1',
        aws_access_key_id=os.environ['AWS_WSDS3_KEY'],
        aws_secret_access_key=os.environ['AWS_WSDS3_SECRET']
        )


    ## Get a sample logfile FILENAME from the db
    ## This only gets the FILENAME that was used to name the file in s3
    ## This code is generated automatically by web2py
    ## for now by id, but maybe later by device
    log_file_name=db(db.log_files.id==request.args[0]).select().first().log_file

    ## connect to the bucket where we store logfiles
    ## boto has good docs for what get_bucket does and the other connection attributes
    bucket=conn.get_bucket('wantsomedashboards')

    ## key is what boto uses to refer to items in the bucket, in this case it is a gzip file
    ## because I'm storing the logfiles in a folder of the bucket, the folder name is being added
    ## manually here. 
    ## logfile='logfiles/log_files.log_file.800bed7f7f8c2857.6d622d3235302e35354231463331455f332e6c6f672e677a.gz'
    ## key=bucket.get_key(logfile)
    key=bucket.get_key('logfiles/'+log_file_name)

    ## Thank you unutbu
    ## http://stackoverflow.com/questions/4204604/how-can-i-create-a-gzipfile-instance-from-the-file-like-object-that-urllib-url
    ## I used the above link to figure out how to actually get the gzip file to behave like a normal decoded file handle in python
    fh = gzip.GzipFile(fileobj=io.BytesIO(key.read()))


    data_LOD=[]

    lines=fh.readlines()

    device_fields_collect=[4,-2,-1]
    # device_fields_collect='ALL'


    conn_dynamo=boto.dynamodb2.connect_to_region(
        'us-east-1',
        aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
        aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET'],
        )

    timeseriestable = Table('timeseriestable',connection=conn_dynamo)

    with timeseriestable.batch_write() as batch:

        for line in lines:
            line = line.strip()
            cells = line.split(',')

            device_id = 'TEST_3'
            timestamp = cells[0][1:-1]

            data=dict(
                timeseriesname=device_id,
                timestamp=timestamp,
                )

            if device_fields_collect=='ALL':
                for index in range(len(cells)):
                    data[device_id+'__'+str(index)]=cells[int(index)]

            else:
                for index in device_fields_collect:
                    if index<0:
                        index = len(cells)+index
                    data[device_id+'__'+str(index)]=cells[int(index)]

            data_LOD.append(data)

            batch.put_item(data)


    return locals()








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

        data=dict()
        for key in entry.keys():
            data[key]=entry[key]



        # timeserieslist.append(
        #                         [
        #                             entry['timeseriesname'],
        #                             entry['timestamp'],
        #                             # entry['cumulative_electric_usage_kwh']
        #                         ]
        #                     )

        timeserieslist.append(data)

    items=int(request.vars['length'])
    start=int(request.vars['start'])
    draw=int(request.vars['draw'])
    end=start+items









    time=datetime.now()

    ## This and the actual field names should come from a config table
    ## I'm seeing a table with device type, and then field index, and field name
    fake_num_fields=114

    device_id=request.args[0]

    ## This says - look in db table device config for a device with id device_id, then from the records that match (should be 1), 
    ## only select the field device_field_groups. Take the first record (again, should only be one) and give me just the value
    ## without the dot operator at the end it would be a dictionary
    device_field_group = db(db.device_config.device_id==device_id).select(db.device_config.device_field_groups).first().device_field_groups

    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Device field group: " + str(device_field_group)

    ## So we have the name of the group
    ## Now we can get the fields that we want to collect
    device_fields_collect = db(db.device_field_groups.field_group_name==device_field_group).select().first().field_group_columns

    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Device fields collect:" + str(device_fields_collect)


    column_names=[]
    if device_fields_collect=='ALL':
        for index in range(len(cells)):
            column_name=device_id+"__"+str(index)
            column_names.append(column_name)
            # data[device_id+'__'+str(index)]=cells[int(index)]

    else:
        for index in device_fields_collect:
            if index<0:
                index = fake_num_fields+index
            # data[device_id+'__'+str(index)]=cells[int(index)]
            column_name=device_id+"__"+str(index)
            column_names.append(column_name)

    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Field names:\n"+str(column_names)










    data_dict=dict(
        draw=draw,
        recordsTotal=len(timeserieslist),
        recordsFiltered=len(timeserieslist),
        data=timeserieslist[start:end],
        # column_names=column_names,
        )




    #return dict(timeserieslist=timeserieslist)
    # print json.dumps(data_dict)
    # return json.dumps(timeserieslist)
    return json.dumps(data_dict)



def ajax_get_device_field_names():
    import json
    from datetime import datetime
    time=datetime.now()

    ## This and the actual field names should come from a config table
    ## I'm seeing a table with device type, and then field index, and field name
    fake_num_fields=114

    device_id=request.args[0]

    ## This says - look in db table device config for a device with id device_id, then from the records that match (should be 1), 
    ## only select the field device_field_groups. Take the first record (again, should only be one) and give me just the value
    ## without the dot operator at the end it would be a dictionary
    device_field_group = db(db.device_config.device_id==device_id).select(db.device_config.device_field_groups).first().device_field_groups

    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Device field group: " + str(device_field_group)

    ## So we have the name of the group
    ## Now we can get the fields that we want to collect
    device_fields_collect = db(db.device_field_groups.field_group_name==device_field_group).select().first().field_group_columns

    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Device fields collect:" + str(device_fields_collect)


    column_names=[]
    if device_fields_collect=='ALL':
        for index in range(len(cells)):
            column_name=device_id+"__"+str(index)
            column_names.append(column_name)
            # data[device_id+'__'+str(index)]=cells[int(index)]

    else:
        for index in device_fields_collect:
            if index<0:
                index = fake_num_fields+index
            # data[device_id+'__'+str(index)]=cells[int(index)]
            column_name=device_id+"__"+str(index)
            column_names.append(column_name)

    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Field names:\n"+str(column_names)

    column_LOD=[
            dict(data="timeseriesname",title='DEVICE ID'),
            dict(data="timestamp", title='TIMESTAMP'),
    ]

    for item in column_names:
        column_LOD.append(
            dict(
                data=item,
                defaultContent="",
                title=item,
            )
        )

    return json.dumps(column_LOD)



def ajax_graph_aws_timeseries():
    import boto.dynamodb2
    from boto.dynamodb2.table import Table
    import os, json
    from datetime import datetime

    time = datetime.now()

    # print request.vars

    conn=boto.dynamodb2.connect_to_region(
        'us-east-1',
        aws_access_key_id=os.environ['AWS_DYNAMO_KEY'],
        aws_secret_access_key=os.environ['AWS_DYNAMO_SECRET']
        )

    tst = Table('timeseriestable',connection=conn)

    timeseriesname=request.args[0]
    # timeseriesname='001EC600229C_250'

    device_id=request.args[0]

    timeseriesdata=tst.query_2(
        timeseriesname__eq=timeseriesname,
        consistent=True,
        )

    # timeserieslist=[]
    # datalist=[]
    # for entry in timeseriesdata:
    #     if entry['timestamp'][0]=="'":
    #         timeserieslist.append([
    #                     entry['timeseriesname'],
    #                     entry['timestamp'][1:-1],
    #                     entry['cumulative_electric_usage_kwh']
    #                     ])
    #     else:
    #        timeserieslist.append([
    #                     entry['timeseriesname'],
    #                     entry['timestamp'],
    #                     entry['cumulative_electric_usage_kwh']
    #                     ])

    #     datalist.append(entry['cumulative_electric_usage_kwh'])

    timeserieslist=[]

    for entry in timeseriesdata:

        data=dict()
        for key in entry.keys():
            data[key]=entry[key]

        timeserieslist.append(data)



    ## This and the actual field names should come from a config table
    ## I'm seeing a table with device type, and then field index, and field name
    fake_num_fields=114

    ## This says - look in db table device config for a device with id device_id, then from the records that match (should be 1), 
    ## only select the field device_field_groups. Take the first record (again, should only be one) and give me just the value
    ## without the dot operator at the end it would be a dictionary
    device_field_group = db(db.device_config.device_id==device_id).select(db.device_config.device_field_groups).first().device_field_groups

    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Device field group: " + str(device_field_group)

    ## So we have the name of the group
    ## Now we can get the fields that we want to collect
    device_fields_collect = db(db.device_field_groups.field_group_name==device_field_group).select().first().field_group_columns

    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Device fields collect:" + str(device_fields_collect)


    column_names=[]
    if device_fields_collect=='ALL':
        for index in range(len(cells)):
            column_name=device_id+"__"+str(index)
            column_names.append(column_name)
            # data[device_id+'__'+str(index)]=cells[int(index)]

    else:
        for index in device_fields_collect:
            if index<0:
                index = fake_num_fields+index
            # data[device_id+'__'+str(index)]=cells[int(index)]
            column_name=device_id+"__"+str(index)
            column_names.append(column_name)

    print "["+str(time)+"] "+"["+str(device_id)+"] "+"Field names:\n"+str(column_names)



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
    return json.dumps(dict(column_names=column_names, data=timeserieslist[-100:]))
    # return json.dumps(data_dict)




def d3play():
    return dict()

def device():
    device_id=request.args[0]
    return dict(device_id=device_id)


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



def das_test():
    # das_list=list(db().select(db.das_config.das_id)
    # if '001EC600229C' in das_list:
    #     print "yay"
    # return dict(das_list=das_list)

    device_id=request.args[0]

    device_field_group = db(db.device_config.device_id==device_id).select(db.device_config.device_field_groups).first().device_field_groups

    device_fields_collect = db(db.device_field_groups.field_group_name==device_field_group).select().first().field_group_columns

    # list[int(slice[:slice.index(':')]):int(slice[slice.index(':')+1:])]

    return dict(var1=device_field_group, var2=device_fields_collect)