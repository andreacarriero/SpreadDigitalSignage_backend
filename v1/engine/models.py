from util.db import db

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