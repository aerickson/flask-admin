import os
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
        PeeweeUserDatastore, UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
#from flask_admin.contrib import sqla
from flask_admin import helpers as admin_helpers

import peewee

import flask_admin as admin
from flask_admin.contrib.peewee import ModelView


# Create Flask application
app = Flask(__name__)
app.config.from_pyfile('config.py')

#db = SQLAlchemy(app)
db = peewee.SqliteDatabase('test.sqlite', check_same_thread=False)

# Define models
#roles_users = db.Table(
#    'roles_users',
#    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
#    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
#)


#class Role(db.Model, RoleMixin):
#    id = db.Column(db.Integer(), primary_key=True)
#    name = db.Column(db.String(80), unique=True)
#    description = db.Column(db.String(255))
#
#    def __str__(self):
#        return self.name
#
#
#class User(db.Model, UserMixin):
#    id = db.Column(db.Integer, primary_key=True)
#    first_name = db.Column(db.String(255))
#    last_name = db.Column(db.String(255))
#    email = db.Column(db.String(255), unique=True)
#    password = db.Column(db.String(255))
#    active = db.Column(db.Boolean())
#    confirmed_at = db.Column(db.DateTime())
#    roles = db.relationship('Role', secondary=roles_users,
#                            backref=db.backref('users', lazy='dynamic'))
#
#    def __str__(self):
#        return self.email

class BaseModel(peewee.Model):
    class Meta:
        database = db


class User(BaseModel):
    username = peewee.CharField(max_length=80)
    email = peewee.CharField(max_length=120)

    def __unicode__(self):
        return self.username

class Role(BaseModel, RoleMixin):
    name = peewee.CharField(unique=True)
    description = peewee.TextField(null=True)

class UserRoles(BaseModel):
    user = peewee.ForeignKeyField(User, related_name='roles')
    role = peewee.ForeignKeyField(Role, related_name='users')
    name = property(lambda self: self.role.name)
    description = property(lambda self: self.role.description)

#class UserInfo(BaseModel):
#    key = peewee.CharField(max_length=64)
#    value = peewee.CharField(max_length=64)
#
#    user = peewee.ForeignKeyField(User, related_name='user_info')
#
#    def __unicode__(self):
#        return '%s - %s' % (self.key, self.value)

class Post(BaseModel):
    title = peewee.CharField(max_length=120)
    text = peewee.TextField(null=False)
    date = peewee.DateTimeField()

    user = peewee.ForeignKeyField(User)

    def __unicode__(self):
        return self.title


class UserAdmin(ModelView):
#    inline_models = (UserInfo,)
    pass


class PostAdmin(ModelView):
    # Visible columns in the list view
    column_exclude_list = ['text']

    # List of columns that can be sorted. For 'user' column, use User.email as
    # a column.
    column_sortable_list = ('title', ('user', User.email), 'date')

    # Full text search
    column_searchable_list = ('title', User.username)

    # Column filters
    column_filters = ('title',
                      'date',
                      User.username)

    form_ajax_refs = {
        'user': {
            'fields': (User.username, 'email')
        }
    }




# Setup Flask-Security
#user_datastore = SQLAlchemyUserDatastore(db, User, Role)
user_datastore = PeeweeUserDatastore(db, User, Role, UserRoles)

security = Security(app, user_datastore)


# Create customized model view class
#class MyModelView(sqla.ModelView):
#
#    def is_accessible(self):
#        if not current_user.is_active or not current_user.is_authenticated:
#            return False
#
#        if current_user.has_role('superuser'):
#            return True
#
#        return False
#
#    def _handle_view(self, name, **kwargs):
#        """
#        Override builtin _handle_view in order to redirect users when a view is not accessible.
#        """
#        if not self.is_accessible():
#            if current_user.is_authenticated:
#                # permission denied
#                abort(403)
#            else:
#                # login
#                return redirect(url_for('security.login', next=request.url))
#

# Flask views
@app.route('/')
def index():
    return render_template('index.html')

# Create admin
#admin = flask_admin.Admin(
#    app,
#    'Example: Auth',
#    base_template='my_master.html',
#    template_mode='bootstrap3',
#)

# Add model views
#admin.add_view(MyModelView(Role, db.session))
#admin.add_view(MyModelView(User, db.session))

#admin = admin.Admin(app, name='Example: Peewee')

#admin.add_view(UserAdmin(User))
#admin.add_view(PostAdmin(Post))

# define a context processor for merging flask-admin's template context into the
# flask-security views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for
    )


def build_sample_db():
    """
    Populate a small db with some example entries.
    """

    import string
    import random

    db.drop_all()
    db.create_all()

    with app.app_context():
        user_role = Role(name='user')
        super_user_role = Role(name='superuser')
        db.session.add(user_role)
        db.session.add(super_user_role)
        db.session.commit()

        test_user = user_datastore.create_user(
            first_name='Admin',
            email='admin',
            password=encrypt_password('admin'),
            roles=[user_role, super_user_role]
        )

        first_names = [
            'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie', 'Sophie', 'Mia',
            'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
            'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
        ]
        last_names = [
            'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
            'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
            'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
        ]

        for i in range(len(first_names)):
            tmp_email = first_names[i].lower() + "." + last_names[i].lower() + "@example.com"
            tmp_pass = ''.join(random.choice(string.ascii_lowercase + string.digits) for i in range(10))
            user_datastore.create_user(
                first_name=first_names[i],
                last_name=last_names[i],
                email=tmp_email,
                password=encrypt_password(tmp_pass),
                roles=[user_role, ]
            )
        db.session.commit()
    return

if __name__ == '__main__':

    # Build a sample db on the fly, if one does not exist yet.
    #app_dir = os.path.realpath(os.path.dirname(__file__))
    #database_path = os.path.join(app_dir, app.config['DATABASE_FILE'])
    #if not os.path.exists(database_path):
    #    build_sample_db()

    import logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    admin = admin.Admin(app, name='Example: Peewee')

#    admin.add_view(UserAdmin(User))
#    admin.add_view(PostAdmin(Post))

    admin.add_view(UserAdmin(User))
    admin.add_view(UserAdmin(Role))

    try:
        User.create_table()
        UserRoles.create_table()
        Role.create_table()
        #UserInfo.create_table()
        #Post.create_table()
    except:
        pass

    # Start app
    app.run(debug=True)
