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
                'description',
                 'college_location']
                )
    if grid.process().accepted:
        session.flash = T('Post Added')
        redirect(URL('default', 'posting', args='all'))
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
    db.listing.id.readable=False
    db.listing.sold.readable=False
    db.listing.likes.readable=False
    db.listing.date_posted.readable=False
    db.listing.seller.readable=False

    p = db.listing(request.args(0)) or redirect(URL('default', 'posting'))
    if int(p.user_id) != auth.user_id:
        session.flash = T('You are not authorized!')
        redirect(URL('default', 'posting'))
    grid = SQLFORM(db.listing, record=p, showid=False,
                fields =['item',
                        'category',
                        'price',
                        'image',
                        'description'])
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
    print(request.vars.category)
    if int(p.user_id) != auth.user.id:
        session.flash = T('You are not authorized!')
        redirect(URL('default', 'posting', args=[p.category]))
    # confirm = FORM.confirm('delete listing')
    grid = SQLFORM(db.listing, record = p, readonly = True, upload = URL('download'))
    # if confirm.accepted:
    db(db.listing.id == p.id).delete()
    session.flash = T('listing is deleted')
    redirect(URL('default', 'posting', args=[p.category]))
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
        if auth.user and auth.user.id == int(row.user_id):
            b = A('Delete', _class='btn btn-secondary', _href=URL('default', 'delete', args=[row.id], vars=dict(category='row.category'), user_signature=True))
        return b

    def editButton(row):
        b = ''
        if auth.user and auth.user.id == int(row.user_id):
            b = A('Edit', _class='btn btn-primary', _href=URL('default', 'edit', args=[row.id]))
        return b

    def soldButton(row):
        b = ''
        if auth.user and auth.user.id == int(row.user_id):
            b = A('Sold/Not Sold', _class='btn btn-warning', _href=URL('default', 'soldCheck', args=[row.id], user_signature=True))
        return b

    def viewButton(row):
        b = A('View', _class='btn btn-success', _href=URL('default','view_page',args=[row.id]))
        return b

    def profileButton(row):
        b = A('Profile', _class='btn btn-info', _href=URL('default','seller_profile',args=[row.id]))
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
                db.listing.date_posted
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

    add = A('Add Post', _class='btn btn-info', _href=URL('default', 'add'))
    return dict(grid=grid, add=add)

#Gets info for other profile
@auth.requires_login()
def seller_profile():
    p = db.listing(request.args(0)) or redirect(URL('default', 'seller_profile'))
    post_id = request.args(0)
    info = db(db.listing.id == post_id).select().first()
    seller_email =  info.email
    profile_info = db(db.auth_user.email==seller_email).select().first()
    return dict(p=p,profile=profile_info)

#Gets the item information and profile info to show on page
def view_page():
    p = db.listing(request.args(0)) or redirect(URL('default', 'view_page'))
    post_id = request.args(0)
    item_info = db(db.listing.id == post_id).select().first()
    user_info = item_info.email
    profile_info = db(db.auth_user.email==user_info).select().first()
    available = item_info.sold
    if available == False:
        verdict = "Yes"
    elif available == True:
        verdict = "No"
    form = SQLFORM(db.messages,
                   fields=['message_content',
                           'date_sent']
                   )
    return dict(p=p,item=item_info,profile=profile_info, verdict = verdict,form=form)

#Retrieves posts in order to display them
@auth.requires_login()    
def saved_posts():
    posts = db(db.saved_posts.user_id == auth.user.id).select()
    temp = []
    for row in posts:
        temp.append(db(db.listing.id == row.listing_id).select().first())

    return dict(posts=temp)

#Used to get all of the messages in order to display on screen
@auth.requires_login()    
def inbox():
    messages = db(db.messages.receiver_id == auth.user.id).select(join=db.listing.on(db.messages.listing_id == db.listing.id))
    # temp = []
    # for row in posts:
    #     temp.append(db(db.listing.id == row.listing_id).select().first())

    return dict(messages=messages)

#self explanatory
def display_posts():
    if request.args(0) == 'all':
        posts = db().select(db.listing.ALL)
    else:
        posts = db(db.listing.category == request.args(0)).select()
    print(request.args(0))
    return dict(posts=posts)

#retrieves the listing_id and deletes the message
def erase_message():
    id = request.args(0)
    db(db.messages.id == id).delete()
    p = redirect(URL('default', 'inbox'))
    return dict(p=p)

#Used for erasing listing and other messages linked to listing_id
def accept_trans():
    id = request.args(0)
    db(db.messages.listing_id == id).delete()
    db(db.listing.id == id).delete()
    p = redirect(URL('default', 'index'))

    return dict(p=p)
