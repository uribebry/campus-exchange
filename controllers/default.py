# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    # response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def user_bar():
    action = '/user'
    if auth.user:
        logout=A('logout', _href=action+'/logout')
        profile=A('profile', _href=action+'/profile')
        password=A('change password', _href=action+'/change_password')
        bar = SPAN(auth.user.email, ' | ', profile, ' | ', password, ' | ', logout, _class='auth_navbar')
    else:
        login=A('login', _href=action+'/login')
        register=A('register',_href=action+'/register')
        lost_password=A('lost password', _href=action+'/request_reset_password')
        bar = SPAN(' ', login, ' | ', register, ' | ', lost_password, _class='auth_navbar')
    return bar


def user():
    test = "PLUG--IN"
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth(), test=test)


@auth.requires_login()
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

@auth.requires_login()
def add():
    #Function to add a listing
    grid = SQLFORM(db.listing,
        fields= ['item',
                'category',
                'price',
                'image',
                'description']
                )
    if grid.process().accepted:
        session.flash = T('Post Added')
        redirect(URL('default', 'index'))
    elif grid.errors:
        session.flash = T('Please correct the info')
    export_classes = dict(csv=True, json=False, html=False,
    tsv=False, xml=False, csv_with_hidden_cols=False,
    tsv_with_hidden_cols=False)
    return dict(grid=grid)

@auth.requires_login()    
def view():
    # Function to view a listing
    p = db.listing(request.args(0)) or redirect(URL('default', 'posting'))
    grid = SQLFORM(db.listing, record = p, readonly = True)
    button = A('return to listings', _class='btn btn-default', _href=URL('default', 'posting'))
    export_classes = dict(csv=True, json=False, html=False,
    tsv=False, xml=False, csv_with_hidden_cols=False,
    tsv_with_hidden_cols=False)
    return dict(p=p, button = button)

@auth.requires_login()
def edit():
    #Function to edit listings
    p = db.listing(request.args(0)) or redirect(URL('default', 'posting'))
    if p.user_id != auth.user_id:
        session.flash = T('You are not authorized!')
        redirect(URL('default', 'posting'))
    grid = SQLFORM(db.listing, record=p)
    if grid.process().accepted:
        session.flash = T('updated')
        redirect(URL('default', 'posting', args=[p.id]))
    export_classes = dict(csv=True, json=False, html=False,
    tsv=False, xml=False, csv_with_hidden_cols=False,
    tsv_with_hidden_cols=False)
    return dict(grid=grid)

@auth.requires_login()
@auth.requires_signature()
def delete():
    #Function to delete listings
    p = db.listing(request.args(0)) or redirect(URL('default', 'posting'))
    if p.user_id != auth.user_id:
        session.flash = T('You are not authorized!')
        redirect(URL('default', 'posting', args=[p.category]))
    # confirm = FORM.confirm('delete listing')
    grid = SQLFORM(db.listing, record = p, readonly = True, upload = URL('download'))
    # if confirm.accepted:
    db(db.listing.id == p.id).delete()
    session.flash = T('listing is deleted')
    redirect(URL('default', 'posting',args=[p.category]))
    export_classes = dict(csv=True, json=False, html=False,
    tsv=False, xml=False, csv_with_hidden_cols=False,
    tsv_with_hidden_cols=False)
    return dict(p=p, grid=grid, confirm=confirm)

@auth.requires_login()
@auth.requires_signature()
def soldCheck():
    #an item to show the user the avalibility of a product
    row = request.args(0)
    item = db.listing(request.args(0)) or redirect(URL('default', 'posting'))
    item.update_record(sold = not item.sold) 
    redirect(URL('default', 'posting', args=[item.category]))

def posting():
    #the posting to show the grid
    links = []
    q = (db.listing) if request.args(0) == 'all' else db(db.listing.category == request.args(0))

    export_classes = dict(csv=True, json=False, html=False,
         tsv=False, xml=False, csv_with_hidden_cols=False,
         tsv_with_hidden_cols=False)

    def deleteButton(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('Delete', _class='btn btn-info', _href=URL('default', 'delete', args=[row.id], user_signature=True))
        return b

    def editButton(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('Edit', _class='btn btn-info', _href=URL('default', 'edit', args=[row.id]))
        return b

    def soldButton(row):
        b = ''
        if auth.user_id == row.user_id:
            b = A('Sold/Not Sold', _class='btn btn-info', _href=URL('default', 'soldCheck', args=[row.id], user_signature=True))
        return b

    def viewButton(row):
        b = A('View', _class='btn btn-info', _href=URL('default','view',args=[row.id]))
        return b

    def profileButton(row):
        b = A('Profile', _class='btn btn-info', _href=URL('default','profile',args=[row.user_id]))
        return b
    
    # all the buttons for posting.html
    links = [
        dict(header='', body = viewButton),
        dict(header='', body = profileButton),
        dict(header='', body = deleteButton),
        dict(header='', body = editButton),
        dict(header='', body = soldButton),
        ]

    # start_idx = 1 if show_all else 0
    export_classes = dict(csv=True, json=False, html=False,
    tsv=False, xml=False, csv_with_hidden_cols=False,
    tsv_with_hidden_cols=False)

# declear the grid once
    grid = SQLFORM.grid(q,
        args=request.args[:1],
        fields=[db.listing.sold,
                db.listing.seller,
                db.listing.college_location,
                db.listing.item,
                db.listing.description,
                db.listing.price,
                db.listing.user_id,
                # db.listing.date_posted
                ],
        links=links,
        editable=False,
        deletable=False,
        csv=False,
        details=False,
        create=False,
        maxtextlength=50,
        paginate=15
        )

    add = A('Add Post', _class='btn btn-default', _href=URL('default', 'add'))

    return dict(grid=grid, add=add)


