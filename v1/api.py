from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify
from flask_restful_swagger_2 import Api, Resource, swagger
from passlib.hash import pbkdf2_sha256

import v1.engine
from v1.engine.messages import Messages
from v1.engine.models import User
from v1.engine.models import Screen as ScreenModel
from v1.engine.models import ScreenGroup as ScreenGroupModel

from util.db import db

#Logging
import logging
import util.logger
log = logging.getLogger('APIv1.0')

apiVersion = '1.0'

app = Blueprint('apiv1', __name__)
api = Api(app, api_version=apiVersion, base_path='/api/v1', api_spec_url='/spec')

#Auth
def hash(password):
	return pbkdf2_sha256.encrypt(password, rounds=20000, salt_size=16)

@app.route('/docs')
def render_docs():
    log.info('Rendering api docs')
    return '<!DOCTYPE html><html><head><title>API Docs</title><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"><style>body {margin: 0; padding: 0;}</style></head><body><redoc spec-url="spec.json"></redoc><script src="https://rebilly.github.io/ReDoc/releases/latest/redoc.min.js"> </script></body></html>'


class Version(Resource):
    @swagger.doc({
        'tags': ['api'],
        'description': 'Get current API version',
        'responses': {
            '200': {
                'description': 'Ok',
                'examples': {
                    'application/json': {
                        'engine_version': '1.0',
                        'api_version': '1.0'
                    }
                }
            }
        }
    })
    def get(self):
        return {
                'engine_version': v1.engine.engine_version,
                'api_version': apiVersion
                }


class Auth(Resource):

    @swagger.doc({
        'tags': ['authentication'],
        'description': 'Check if user is authenticated',
        'responses': {
            '200': {
                'description': 'User',
                'examples': {
                    'application/json': {
                        'user': User.doc()
                    }
                }
            },
            '404': {
                'description': 'User not found',
                'examples':  {
                    'application/json': {
                        'error': Messages.user_not_found
                    }
                }
            },
            '401': {
                'description': 'Unauthenticated',
                'examples': {
                    'application/json': {
                        'error': Messages.unauthenticated
                    }
                }
            }
        }

    })
    def get(self):
        if session.get('logged_in'):
            user = User.query.filter_by(id=session.get('user_id')).first()
            if user:
                return {
                            'user': user.serialize()
                        }, 200
            else:
                return {
                            'error': Messages.user_not_found
                        }, 404
        else:
            return {
                        'error': Messages.unauthenticated
                    }, 401
    
    @swagger.doc({
        'tags': ['authentication'],
        'description': 'Log user in',
        'parameters': [
            {
                'name': 'email',
                'required': True,
                'description': 'User email',
                'type': 'string',
                'in': 'formData'
            },
            {
                'name': 'password',
                'required': True,
                'description': 'User password',
                'type': 'string',
                'in': 'formData'
            }
        ],
        'responses': {
            '200': {
                'description': 'User logged in',
                'examples': {
                    'application/json': {
                        'user': User.doc()
                    }
                }
            },
            '400': {
                'description': 'Parameters error',
                'examples': {
                    'application/json': {
                        'error': '<error>'
                    }
                }
            },
            '404': {
                'description': 'User not found',
                'examples': {
                    'application/json': {
                        'error': Messages.user_not_found
                    }
                }
            }
        }
    })
    def post(self):
        try:
            email = request.values['email']
            password = request.values['password']
        except Exception as e:
            return {
                        'error': str(e)
                    }, 400

        user = User.query.filter_by(email=email).first()
        if user:
            if pbkdf2_sha256.verify(password, user.password):
                session['logged_in'] = True
                session['user_id'] = user.id

                return {
                            'user': user.serialize()
                        }, 200
        else:
            return {
                        'error': Messages.user_not_found
                    }, 404

    @swagger.doc({
        'tags': ['authentication'],
        'description': 'Register a new user',
        'parameters': [
            {
                'name': 'email',
                'required': True,
                'description': 'User email',
                'type': 'string',
                'in': 'formData'
            },
            { 
                'name': 'password',
                'required': True,
                'description': 'User password',
                'type': 'string',
                'in': 'formData'
            },
            { 
                'name': 'first_name',
                'required': True,
                'description': 'User first name',
                'type': 'string',
                'in': 'formData'
            },
            { 
                'name': 'last_name',
                'required': True,
                'description': 'User last name',
                'type': 'string',
                'in': 'formData'
            }
        ], 
        'responses': {
            '200': {
                'description': 'User registered',
                'examples': {
                    'application/json': {
                        'user': User.doc()
                    }
                }
            },
            '400': {
                'description': 'Parameters error',
                'examples': {
                    'application/json': {
                        'error': '<error>'
                    }
                }
            },
            '409': {
                'description': 'User already exist',
                'examples': {
                    'application/json': {
                        'error': Messages.user_already_exist
                    }
                }
            },
            '500': {
                'description': 'Database error',
                'examples': {
                    'application/json': {
                        'error': '<error>'
                    }
                }
            }

        }
    })
    def put(self):
        try:
            email = request.values['email']
            password = request.values['password']
            first_name = request.values['first_name']
            last_name = request.values['last_name']
        except Exception as e:
            return {
                        'error': str(e)
                    }, 400

        user = User.query.filter_by(email=email).first()
        if user:
            return {
                        'error': Messages.user_already_exist
                    }, 409
            
        try:
            user = User(email=email, password=hash(password), first_name=first_name, last_name=last_name)
            db.session.add(user)
            db.session.commit()
            return {
                        'user': user.serialize()
                    }, 200

        except Exception as e:
            return {
                        'error': str(e)
                    }, 500
    
    @swagger.doc({
        'tags': ['authentication'],
        'description': 'Log user out', 
        'responses': {
            '200': {
                'description': 'Logged out',
                'examples': {
                    'application/json': {
                        'message': Messages.logged_out
                    }
                }
            },
            '401': {
                'description': 'Unauthenticated',
                'examples': {
                    'application/json': {
                        'error': Messages.unauthenticated
                    }
                }
            }
        }
    })
    def delete(self):
        if session.get('logged_in'):
            session['logged_in'] = False
            session['user_id'] = None
            return {
                        'message': Messages.logged_out
                    }, 200
        else:
            return {
                        'error': Messages.unauthenticated
                    }, 401


class Screen(Resource):

    @swagger.doc({
        'tags': ['screen'],
        'description': 'Get all screens',
        'responses': {
            '200': {
                'description': 'Screen list',
                'examples': {
                    'application/json': {
                        'screens': [ScreenModel.doc()]
                    }
                }
            }
        }
    })
    def get(self):
        screens = ScreenModel.query.all()
        screens_list = [screen.serialize() for screen in screens]
        return {
                    'screens': screens_list
                }, 200

    @swagger.doc({
        'tags': ['screen'],
        'description': 'Add new screen',
        'parameters': [
            {
                'name': 'name',
                'required': True,
                'description': 'Screen name',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'location',
                'required': False,
                'description': 'Screen location',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'active',
                'required': False,
                'description': 'If screen is active or not',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'group_id',
                'required': False,
                'description': 'Group id where to add screen',
                'in': 'formData',
                'type': 'integer'
            }
        ],
        'responses': {
            '201': {
                'description': 'Screen created',
                'examples': {
                    'application/json': {
                        'screen': ScreenModel.doc()
                    }
                }
            },
            '400': {
                'description': 'Parameters error',
                'examples': {
                    'application/json': {
                        'error': '<error>'
                    }
                }
            },
            '409': {
                'description': 'Screen already exist',
                'examples': {
                    'application/json': {
                        'error': Messages.screen_already_exist,
                        'screen': ScreenModel.doc()
                    }
                }
            },
            '500': {
                'description': 'Error on item creation',
                'examples': {
                    'application/json': {
                        'error': Messages.database_add_error
                    }
                }
            }
        }
    })
    def put(self):
        try:
            screen_name = request.values['name']
            screen_location = request.values.get('location', None)
            screen_group_id = request.values.get('group_id', None)
        except Exception as e:
            return {'error': str(e)}, 400

        screen = ScreenModel.query.filter_by(name=screen_name).first()
        if screen:
            return {
                    'error': Messages.screen_already_exist,
                    'screen': screen.serialize()
                    }, 409

        try:
            screen = ScreenModel(screen_name, screen_location, screen_group_id)
            db.session.add(screen)
            db.session.commit()
            return {
                        'screen': screen.serialize()    
                    }, 201
        except Exception as e:
            return {'error': Messages.database_add_error}, 500
        

class ScreenItem(Resource):

    @swagger.doc({
        'tags': ['screen'],
        'description': 'Get screen details',
        'parameters': [
            {
                'name': 'screen_id',
                'required': True,
                'description': 'Screen ID',
                'in': 'path',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Screen',
                'examples': {
                    'application/json': {
                        'screen': ScreenModel.doc()
                    }
                }
            },
            '404': {
                'description': 'Screen not found',
                'examples': {
                    'application/json': {
                        'error': Messages.screen_not_found
                    }
                }
            }
        }
    })
    def get(self, screen_id):
        screen = ScreenModel.query.filter_by(id=screen_id).first()
        if screen:
            return {
                        'screen': screen.serialize()
                    }, 200
        else:
            return {
                        'error': Messages.screen_not_found
                    }, 404

    @swagger.doc({
        'tags': ['screen'],
        'description': 'Update screen datails',
        'parameters': [
            {
                'name': 'screen_id',
                'required': True,
                'description': 'Screen ID',
                'in': 'path',
                'type': 'integer'
            },
            {
                'name': 'name',
                'required': False,
                'description': 'Screen name',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'location',
                'required': False,
                'description': 'Screen location',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'active',
                'required': False,
                'description': 'If screen is active or not',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'group_id',
                'required': False,
                'description': 'Group id where to add screen',
                'in': 'formData',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Screen updated',
                'examples': {
                    'application/json': {
                        'screen': ScreenModel.doc()
                    }
                }
            },
            '404': {
                'description': 'Screen not found',
                'examples': {
                    'application/json': {
                        'error': Messages.screen_not_found
                    }
                }
            }
        }
    })
    def post(self, screen_id):
        screen = ScreenModel.query.filter_by(id=screen_id).first()
        if screen:
            screen.name = request.values.get('name', screen.name)
            screen.location = request.values.get('location', screen.location)
            screen.active = request.values.get('active', screen.active)
            screen.group_id = request.values.get('group_id', screen.group_id)
            db.session.commit()
            return {'screen': screen.serialize()}, 200
        else:
            return {'error': Messages.screen_not_found}, 404

    @swagger.doc({
        'tags': ['screen'],
        'description': 'Mark screen as inactive',
        'parameters': [
            {
                'name': 'screen_id',
                'required': True,
                'description': 'Screen ID',
                'in': 'path',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Screen deleted',
                'examples': {
                    'application/json': {
                        'screen': ScreenModel.doc()
                    }
                }
            },
            '404': {
                'description': 'Screen not found',
                'examples': {
                    'application/json': {
                        'error': Messages.screen_not_found
                    }
                }
            }
        }
    })
    def delete(self, screen_id):
        screen = ScreenModel.query.filter_by(id=screen_id).first()
        if screen:
            screen.active = False
            db.session.commit()
            return {'screen': screen.serialize()}, 200
        else:
            return {'error': Messages.screen_not_found}, 404

class ScreenGroup(Resource):

    @swagger.doc({
        'tags': ['screengroup'],
        'description': 'Get screen groups',
        'responses': {
            '200': {
                'description': 'Groups list',
                'examples': {
                    'application/json': {
                        'groups': [ScreenGroupModel.doc()]
                    }
                }
            }
        }
    })
    def get(self):
        groups = ScreenGroupModel.query.all()
        groups_list = [group.serialize() for group in groups]

        return {
                    'groups': groups_list
                }, 200


api.add_resource(Version, '/version')
api.add_resource(Auth, '/auth')
api.add_resource(Screen, '/screen')
api.add_resource(ScreenItem, '/screen/<int:screen_id>')
api.add_resource(ScreenGroup, '/group')