from util.db import db
from uuid import uuid4

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password = db.Column(db.String(120))
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    active = db.Column(db.Boolean(), default=False)

    def __init__(self, email, password, first_name=None, last_name=None, active=False):
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.active = active

    def serialize(self):
        return {
                    'email': self.email,
                    'first_name': self.first_name,
                    'last_name': self.last_name,
                    'active': self.active
                }
    
    @staticmethod
    def doc():
        return {
                    'email': '<User email address>',
                    'firs_name': '<User first name>',
                    'last_name': '<User last name>', 
                    'active': 'True/False'
                }

class ScreenGroup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    location = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True) 

    def __init__(self, name, location, active=True):
        self.name = name
        self.location = location
        self.active = active

    def serialize(self):
        members = Screen.query.filter_by(group_id=self.id).all()
        members_list = [screen.serialize() for screen in members]

        return {
                    'id': self.id,
                    'name': self.name,
                    'location': self.location,
                    'active': self.active,
                    'members': members_list
                }

    @staticmethod
    def doc():
        return {
                    'id': '<Group id>',
                    'name': '<Group name>',
                    'location': '<Group location>',
                    'active': 'True/False',
                    'members': [Screen.doc()]
                }


class Screen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    location = db.Column(db.String(100))
    group_id = db.Column(db.Integer(), db.ForeignKey('screen_group.id'))
    active = db.Column(db.Boolean, default=True)

    def __init__(self, name, location=None, group_id=None, active=True):
        self.name = name
        self.location = location
        self.group_id = group_id
        self.active = active

    def serialize(self):
        return {
                    'id': self.id,
                    'name': self.name,
                    'location': self.location,
                    'active': self.active,
                    'group_id': self.group_id
                }

    @staticmethod
    def doc():
        return {
                    'id': '<Screen id>',
                    'name': '<Screen name>',
                    'location': '<Screen location>',
                    'active': 'True/False',
                    'group_id': '<Group id>'
                }
