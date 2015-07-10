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

    from datetime import datetime

    page_name=request.function
    page_vars=request.vars
    page_args=request.args

    counter_data=db(db.page_visit_count.page_name==page_name).select().first()

    if counter_data==None:

        dummy = db.page_visit_count.insert(page_name=page_name, counter=1)
        current_count=1

    else:

        current_count=counter_data.counter
        current_count+=1
        counter_data.update_record(counter=current_count)

    ## This means that its sending acuisuite info - not device info
    if request.vars['MODE']=='STATUS':

        db.debug_tbl.insert(error_message="Recieving Acquisuite Config Info")
        db.page_visit_data.insert(page_name=page_name,last_visited=datetime.now(), vars=page_vars, args=page_args)
        db.commit()

    ## For right now, this means we are getting data from a device, in the future I will check for the LOGFILE url variable
    else:

        db.debug_tbl.insert(error_message="Recieving Device Info!")

        field_storage_object=request.vars['LOGFILE']
        

        ## If for some reason there isn't actuall a LOGFILE url variable
        if field_storage_object==None:
            status="FAILURE"
            return dict(current_count=current_count, status=status)

        else:
            filename_attr=field_storage_object.name
            db.page_visit_data.insert(page_name=page_name,last_visited=datetime.now(), vars=page_vars, args=page_args, filename=filename_attr, log_file=field_storage_object)

        db.commit()

    return dict(current_count=current_count, status="SUCCESS")