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


    db.debug_tbl.insert(error_message="BEGIN")
    db.commit()

    field_storage_object=request.vars['LOGFILE']
    db.debug_tbl.insert(error_message="Was able to access storage object")
    db.commit()


    filename_attr=field_storage_object.name
    db.debug_tbl.insert(error_message="Was able to access filename attribute", other_info=filename_attr)
    db.commit()

    value_attr=field_storage_object.value
    db.debug_tbl.insert(error_message="Was able to access value attribute", other_info=value_attr)
    db.commit()

    type_attr=field_storage_object.type
    db.debug_tbl.insert(error_message="Was able to access type attribute", other_info=type_attr)
    db.commit()

    type_options_attr=field_storage_object.type_options
    db.debug_tbl.insert(error_message="Was able to access type options attribute", other_info=type_options_attr)
    db.commit()

    disposition_attr=field_storage_object.disposition
    db.debug_tbl.insert(error_message="Was able to access disposition attribute", other_info=disposition_attr)
    db.commit()

    disposition_options_attr=field_storage_object.disposition_options
    db.debug_tbl.insert(error_message="Was able to access disposition options attribute", other_info=disposition_options_attr)
    db.commit()

    headers_attr=field_storage_object.headers
    db.debug_tbl.insert(error_message="Was able to access header attribute", other_info=header_attr)
    db.commit()


    dummy = db.page_visit_data.insert(page_name=page_name,last_visited=datetime.now(), vars=page_vars, args=page_args, filename=filename_attr, log_file=field_storage_object)
    db.commit()

    return dict(current_count=current_count)