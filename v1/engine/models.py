from util.db import db
from uuid import uuid4
import ast

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
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)
    config_v = db.Column(db.Integer)
    config_id = db.Column(db.Integer(), db.ForeignKey('configuration.id'))

    def __init__(self, name, location, active=True, config_id=1):
        self.name = name
        self.location = location
        self.active = active
        self.config_v = 1
        self.config_id = config_id

        #Create dummy configuration if config table is empty
        try:
            confs = Configuration.query.all()
            if not len(confs) >= 1:
                conf = Configuration()
                db.session.add(conf)
                db.session.commit()
                self.config_id = conf.id
        except Exception as e:
            print(e)

    def serialize(self):
        members = Screen.query.filter_by(group_id=self.id, deleted=False).all()
        members_list = [screen.serialize() for screen in members]

        return {
                    'id': self.id,
                    'name': self.name,
                    'location': self.location,
                    'active': self.active,
                    'deleted': self.deleted,
                    'config_id': self.config_id,
                    'members': members_list
                }

    def push_on_the_fly(self):
        self.config_v = self.config_v + 1
        db.session.commit()

    @staticmethod
    def doc():
        return {
                    'id': '<Group id>',
                    'name': '<Group name>',
                    'location': '<Group location>',
                    'active': 'True/False',
                    'deleted': 'True/False',
                    'config_id': '<Config ID>',
                    'members': [Screen.doc()]
                }


class Screen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String(100))
    group_id = db.Column(db.Integer(), db.ForeignKey('screen_group.id'))
    active = db.Column(db.Boolean, default=True)
    deleted = db.Column(db.Boolean, default=False)
    config_v = db.Column(db.Integer)
    config_id = db.Column(db.Integer(), db.ForeignKey('configuration.id'))

    def __init__(self, name, location=None, group_id=None, active=True, config_id=1):
        self.name = name
        self.location = location
        self.group_id = group_id
        self.active = active
        self.config_v = 1
        self.config_id = config_id

        #Create dummy configuration if config table is empty
        try:
            confs = Configuration.query.all()
            if not len(confs) >= 1:
                conf = Configuration()
                db.session.add(conf)
                db.session.commit()
                self.config_id = conf.id
        except Exception as e:
            print(e)

    def serialize(self):
        return {
                    'id': self.id,
                    'name': self.name,
                    'location': self.location,
                    'active': self.active,
                    'deleted': self.deleted,
                    'group_id': self.group_id,
                    'config_id': self.config_id
                }

    def push_on_the_fly(self):
        self.config_v = self.config_v + 1
        if self.group_id:
            group = ScreenGroup.query.filter_by(id=self.group_id).first()
            if group:
                group.push_on_the_fly()
        db.session.commit()

    @staticmethod
    def doc():
        return {
                    'id': '<Screen id>',
                    'name': '<Screen name>',
                    'location': '<Screen location>',
                    'active': 'True/False',
                    'deleted': 'True/False',
                    'group_id': '<Group id>',
                    'config_id': '<Config id>'
                }

class Configuration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    deleted = db.Column(db.Boolean)
    description = db.Column(db.String(2000))

    head_active = db.Column(db.Boolean)
    head_height = db.Column(db.String(10))
    head_fontSize = db.Column(db.String(10))
    head_bgColor = db.Column(db.String(100))
    head_textColor = db.Column(db.String(100))
    head_borderColor = db.Column(db.String(100))
    head_logo_active = db.Column(db.Boolean)
    head_logo_url = db.Column(db.String(1000))
    head_content_active = db.Column(db.Boolean)
    head_content_text = db.Column(db.String(1000))
    head_clock_active = db.Column(db.Boolean)
    head_clock_textColor = db.Column(db.String(100))
    head_clock_bgColor = db.Column(db.String(100))

    bottom_active = db.Column(db.Boolean)
    bottom_content = db.Column(db.String(5000))
    bottom_marquee = db.Column(db.Boolean)
    bottom_height = db.Column(db.String(10))
    bottom_fontSize = db.Column(db.String(10))
    bottom_bgColor = db.Column(db.String(100))
    bottom_textColor = db.Column(db.String(100))

    body_background_bgColor = db.Column(db.String(100))
    body_background_bgImage = db.Column(db.String(2000))
    body_content_fixedContent = db.Column(db.String())
    body_content_columns = db.Column(db.String())

    def __init__(
                    self,
                    deleted = False,
                    description = None,
                    head_active = True,
                    head_height = '70px',
                    head_fontSize = '2em',
                    head_bgColor = '#003459',
                    head_textColor = '#fff',
                    head_borderColor = '#fff',
                    head_logo_active = False,
                    head_logo_url = None,
                    head_content_active = True,
                    head_content_text = 'Digital Signage',
                    head_clock_active = True,
                    head_clock_textColor = '#fff',
                    head_clock_bgColor = '#003459',
                    bottom_active = True,
                    bottom_content = None,
                    bottom_marquee = False,
                    bottom_height = '70px',
                    bottom_fontSize = '2em',
                    bottom_bgColor = '#003459',
                    bottom_textColor = '#fff',
                    body_background_bgColor = '#00A8E8',
                    body_background_bgImage = None,
                    body_content_fixedContent = [],
                    body_content_columns = []
                ):
        self.deleted = deleted
        self.description = description
        self.head_active = head_active
        self.head_height = head_height
        self.head_fontSize = head_fontSize
        self.head_bgColor = head_bgColor
        self.head_textColor = head_textColor
        self.head_borderColor = head_borderColor
        self.head_logo_active = head_logo_active
        self.head_logo_url = head_logo_url
        self.head_content_active = head_content_active
        self.head_content_text = head_content_text
        self.head_clock_active = head_clock_active
        self.head_clock_textColor = head_clock_textColor
        self.head_clock_bgColor = head_clock_bgColor
        self.bottom_active = bottom_active
        self.bottom_content = bottom_content
        self.bottom_marquee = bottom_marquee
        self.bottom_height = bottom_height
        self.bottom_fontSize = bottom_fontSize
        self.bottom_bgColor = bottom_bgColor
        self.bottom_textColor = bottom_textColor
        self.body_background_bgColor = body_background_bgColor
        self.body_background_bgImage = body_background_bgImage
        self.body_content_fixedContent = str(body_content_fixedContent)
        self.body_content_columns = str(body_content_columns)

    def serialize(self):
        return {
                'id': self.id,
                'deleted': self.deleted,
                'description': self.description,
                'head': {
                            'active': self.head_active,
                            'height': self.head_height,
                            'fontSize': self.head_fontSize,
                            'bgColor': self.head_bgColor,
                            'textColor': self.head_textColor,
                            'borderColor': self.head_borderColor,
                            'logo': {
                                'active': self.head_logo_active,
                                'url': self.head_logo_url
                            },
                            'content': {
                                'active': self.head_content_active,
                                'text': self.head_content_text
                            },
                            'clock': {
                                'active': self.head_clock_active,
                                'textColor': self.head_clock_textColor,
                                'bgColor': self.head_clock_bgColor
                            }
                        },
                'bottom': {
                            'active': self.bottom_active,
                            'content': self.bottom_content,
                            'marquee': self.bottom_marquee,

                            'height': self.bottom_height,
                            'fontSize': self.bottom_fontSize,
                            'bgColor': self.bottom_bgColor,
                            'textColor': self.bottom_textColor
                },
                'body': {   
                            'background': {
                                'bgColor': self.body_background_bgColor,
                                'bgImage': self.body_background_bgImage
                            },
                            'content': {
                                'fixedContent': ast.literal_eval(self.body_content_fixedContent),

                                'columns': ast.literal_eval(self.body_content_columns)
                            }
                        }
                }

    @staticmethod
    def doc(deleted=False):
        return {
                'id': 0,
                'deleted': deleted,
                'description': 'Description...',
                'head': {
                            'active': True,
                            'height': '70px',
                            'fontSize': '3em',
                            'bgColor': '#003459',
                            'textColor': '#fff',
                            'borderColor': '#fff',
                            'logo': {
                                'active': True,
                                'url': 'logo.png'
                            },
                            'content': {
                                'active': False,
                                'text': 'Digital Signage'
                            },
                            'clock': {
                                'active': True,
                                'textColor': '#fff',
                                'bgColor': '#003459'
                            }
                        },
                'bottom': {
                            'active': True,
                            'content': 'Lorem ipsum dolor sit amet',
                            'marquee': True,
                            'height': '70px',
                            'fontSize': '2em',
                            'bgColor': '#003459',
                            'textColor': '#fff'
                },
                'body': {   
                            'background': {
                                'bgColor': '#00A8E8',
                                'bgImage': None
                            },
                            'content': {
                                'fixedContent': [
                                    {
                                        'active': True,
                                        'bgColor': '#007EA7',
                                        'textColor': '#fff',
                                        'borderColor': '#fff',
                                        'fontSize': '3em',
                                        'marquee': False,
                                        'content': 'Riunione ore 10 sala 210A'
                                    }
                                ],
                                'columns': [
                                    {
                                        'borderColor': '#fff',
                                        'textColor': '#fff',
                                        'html': 'bla bla'
                                    }                                  
                                ]
                            }
                        }
                }