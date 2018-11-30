# Define your tables below (or better in another model file) for example
#
# >>> db.define_table('mytable', Field('myfield', 'string'))
#
# Fields can be 'string','text','password','integer','double','boolean'
#       'date','time','datetime','blob','upload', 'reference TABLENAME'
# There is an implicit 'id integer autoincrement' field
# Consult manual for more options, validators, etc.

import datetime

def get_user_email():
    return auth.user.email if auth.user is not None else None

def get_date():
    return request.now if auth.user is not None else None

def get_name():
    return auth.user.first_name if auth.user is not None else None

def get_user_id():
    return auth.user.id if auth.user is not None else None

db.define_table('checklist',
                Field('user_email', default=get_user_email()),
                Field('title'),
                Field('memo', 'text'),
                Field('updated_on', 'datetime', update=datetime.datetime.utcnow()),
                Field('is_public', 'boolean', default=False))

db.define_table('listing',
                Field('item'),
                Field('price', 'decimal(6,2)'),
                Field('sold', 'boolean', default=False),
                Field('image', 'upload'),
                Field('seller', default=get_name()),
                Field('user_id', default=get_user_id()),
                Field('phone'),
                Field('email', default=get_user_email()),
                Field('likes', 'integer', default=0),
                Field('description', 'text'),
                Field('college_location'),
                # Field('date_posted', 'date', default=get_date())
                )

db.checklist.user_email.writable = False
db.checklist.user_email.readable = False
db.checklist.updated_on.writable = db.checklist.updated_on.readable = False
db.checklist.id.writable = db.checklist.id.readable = False
# Hides the check box 'is_public' for the user when creating a memo
db.checklist.is_public.readable = db.checklist.is_public.writable = False

db.listing.likes.writable = False
db.listing.user_id.writable = db.listing.user_id.readable = False
db.listing.seller.writable = False
db.listing.phone.writable = db.listing.phone.readable = False
# db.listing.date_posted.writable = False
db.listing.email.writable = db.listing.email.readable = False

# after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
