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
        (T('ADMIN'), False, '#', [

          (T('Admin'), False, URL('admin','site','index')),

          LI(_class='divider'),

          (T('Appadmin'), False, URL('appadmin','index')),

        ]),

        (T('AWS DB'), False, '#', [

          (T('View DAQ Info'), False, URL('aws_table', args=['das_attributes'])),

          LI(_class="divider"),

          (T('View Device Info'), False, URL('aws_table', args=['device_attributes'])),

          LI(_class="divider"),

          # (T('View Tables'), True, '#', [

            # (T('Device Group Fields'), False, URL( 'view_table', vars=dict(table_name='device_field_groups',db='postgres'))),

            # ]),

        ]),
    
    ]

if DEVELOPMENT_MENU: _()

if "auth" in locals(): auth.wikimenu() 
