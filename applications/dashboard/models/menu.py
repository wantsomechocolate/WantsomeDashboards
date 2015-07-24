# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## Customize your APP title, subtitle and menus here
#########################################################################

response.logo = A(B('BATS'),IMG(_class="bat-logo", _src=URL('static','images/bat-logo.png')),
                  _class="navbar-brand wsd-navbar-brand",_href=URL('default','index'),
                  _id="web2py-logo")
response.title = request.application.replace('_',' ').title()
response.subtitle = ''

## read more at http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'James McGlynn <wantsomechocolate@gmail.com>'
response.meta.description = 'BATS'
response.meta.keywords = 'web2py, python, framework'
response.meta.generator = 'Web2py Web Framework'

## your http://google.com/analytics id
response.google_analytics_id = None

#########################################################################
## this is the main application menu add/remove items as required
#########################################################################

response.menu = [
    # (T('Home'), False, URL('default', 'index'), [])
]

DEVELOPMENT_MENU = True

#########################################################################
## provide shortcuts for development. remove in production
#########################################################################

def _():
    # shortcuts
    app = request.application
    ctr = request.controller
    # useful links to internal and external resources
    response.menu += [
        (T('Admin'), False, '#', [

          (T('Admin'), False, URL('admin','site','index')),

          LI(_class='divider'),

          (T('Appadmin'), False, URL('appadmin','index')),

        ]),

        (T('Pages'), False, '#', [

          (T('View DAQ Info'), False, URL('view_aws_info', args=['das_attributes'])),

          LI(_class="divider"),

          (T('View Device Info'), False, URL('view_aws_info', args=['device_attributes'])),

        ]),
    
    ]

if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu() 
