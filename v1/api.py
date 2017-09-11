from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify, abort
from flask_restful_swagger_2 import Api, Resource, swagger
from passlib.hash import pbkdf2_sha256
from uuid import uuid4
from functools import wraps

import v1.engine
from v1.engine.render_client import render_client
from v1.engine.messages import Messages
from v1.engine.models import User
from v1.engine.models import Screen as ScreenModel
from v1.engine.models import ScreenGroup as ScreenGroupModel
from v1.engine.models import Configuration as ConfigurationModel

from util.db import db
from util.str2bool import str2bool

#Logging
import logging
import util.logger
log = logging.getLogger('APIv1.0')

apiVersion = '1.0'

app = Blueprint('apiv1', __name__)
api = Api(app, api_version=apiVersion, base_path='/api/v1', api_spec_url='/spec')

##########
API_KEY = '12345'
API_SECRET = '67890'
##########

#Auth
def hash(password):
    return pbkdf2_sha256.encrypt(password, rounds=20000, salt_size=16)

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kws):
        if request.headers.get('X-Api-Key') == API_KEY and request.headers.get('X-Api-Secret') == API_SECRET:
            pass
        else:
            #return jsonify(message='Unauthorized'), 401
            abort(401)

        return f(*args, **kws)
    return decorated_function


@app.route('/docs')
def render_docs():
    log.info('Rendering api docs')
    return '<!DOCTYPE html><html><head><title>API Docs</title><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"><style>body {margin: 0; padding: 0;}</style></head><body><redoc spec-url="spec.json"></redoc><script src="https://rebilly.github.io/ReDoc/releases/latest/redoc.min.js"> </script></body></html>'

@app.route('/client/<id>')
def get_client(id):
    client = render_client(id)
    return client

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
    @token_required
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
                        'message': Messages.user_not_found
                    }
                }
            },
            '401': {
                'description': 'Unauthenticated',
                'examples': {
                    'application/json': {
                        'message': Messages.unauthenticated
                    }
                }
            }
        }

    })
    def get(self):
        if session.get('logged_in'):
            user = User.query.filter_by(id=session.get('user_id')).first()
            if user:
                return {'user': user.serialize()}, 200
            else:
                return {'message': Messages.user_not_found}, 404
        else:
            return {'message': Messages.unauthenticated}, 401
    
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
                'description': 'Parameters message',
                'examples': {
                    'application/json': {
                        'message': '<error>'
                    }
                }
            },
            '404': {
                'description': 'User not found',
                'examples': {
                    'application/json': {
                        'message': Messages.user_not_found
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
            return {'message': str(e)}, 400

        user = User.query.filter_by(email=email).first()
        if user:
            if pbkdf2_sha256.verify(password, user.password):
                session['logged_in'] = True
                session['user_id'] = user.id

                return {'user': user.serialize()}, 200
        else:
            return {'message': Messages.user_not_found}, 404

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
                        'message': '<error>'
                    }
                }
            },
            '409': {
                'description': 'User already exist',
                'examples': {
                    'application/json': {
                        'message': Messages.user_already_exist
                    }
                }
            },
            '500': {
                'description': 'Database error',
                'examples': {
                    'application/json': {
                        'message': '<error>'
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
            return {'message': str(e)}, 400

        user = User.query.filter_by(email=email).first()
        if user:
            return {'message': Messages.user_already_exist}, 409
            
        try:
            user = User(email=email, password=hash(password), first_name=first_name, last_name=last_name)
            db.session.add(user)
            db.session.commit()
            return {'user': user.serialize()}, 200

        except Exception as e:
            return {'message': str(e)}, 500
    
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
                        'message': Messages.unauthenticated
                    }
                }
            }
        }
    })
    def delete(self):
        if session.get('logged_in'):
            session['logged_in'] = False
            session['user_id'] = None
            return {'message': Messages.logged_out}, 200
        else:
            return {'message': Messages.unauthenticated}, 401


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
    @token_required
    def get(self):
        screens = ScreenModel.query.filter_by(deleted=False).all()
        screens_list = [screen.serialize() for screen in screens]
        return {'screens': screens_list}, 200

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
            },
            {
                'name': 'config_id',
                'required': False,
                'description': 'Configuration ID',
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
                        'message': '<error>'
                    }
                }
            },
            '409': {
                'description': 'Screen already exist',
                'examples': {
                    'application/json': {
                        'message': Messages.screen_already_exist,
                        'screen': ScreenModel.doc()
                    }
                }
            },
            '500': {
                'description': 'Error on item creation',
                'examples': {
                    'application/json': {
                        'message': Messages.database_add_error
                    }
                }
            }
        }
    })
    @token_required
    def post(self):
        try:
            screen_name = request.values['name']
            screen_location = request.values.get('location', None)
            screen_group_id = request.values.get('group_id', None)
            screen_config_id = request.values.get('config_id', 1)
            screen_active = str2bool(request.values.get('active', False))
        except Exception as e:
            return {'message': str(e)}, 400

        if screen_group_id:
            group = ScreenGroupModel.query.filter_by(id=screen_group_id, deleted=False).first()
            if not group:
                return {'message': Messages.screengroup_not_found}, 404

        if screen_config_id:
            config = ConfigurationModel.query.filter_by(id=screen_config_id, deleted=False).first()
            if not config:
                return {'message': Messages.config_not_found}, 404

        screen = ScreenModel.query.filter_by(name=screen_name, deleted=False).first()
        if screen:
            return {
                    'message': Messages.screen_already_exist,
                    'screen': screen.serialize()
                    }, 409

        try:
            screen = ScreenModel(screen_name, screen_location, screen_group_id, active=screen_active)
            screen.config_id = screen_config_id
            db.session.add(screen)
            db.session.commit()
            return {
                        'screen': screen.serialize()    
                    }, 201
        except Exception as e:
            return {'message': Messages.database_add_error}, 500
        

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
                        'message': Messages.screen_not_found
                    }
                }
            }
        }
    })
    @token_required
    def get(self, screen_id):
        screen = ScreenModel.query.filter_by(id=screen_id, deleted=False).first()
        if screen:
            return {
                        'screen': screen.serialize()
                    }, 200
        else:
            return {
                        'message': Messages.screen_not_found
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
            },
            {
                'name': 'config_id',
                'required': False,
                'description': 'Configuration ID',
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
                        'message': Messages.screen_not_found
                    }
                }
            }
        }
    })
    @token_required
    def put(self, screen_id):
        screen = ScreenModel.query.filter_by(id=screen_id, deleted=False).first()
        if screen:
            screen.name = request.values.get('name', screen.name)
            screen.location = request.values.get('location', screen.location)
            screen.active = str2bool(request.values.get('active', screen.active))
            
            screen_config_id = request.values.get('config_id', screen.config_id)
            if screen_config_id:
                config = ConfigurationModel.query.filter_by(id=screen_config_id, deleted=False).first()
                if not config:
                    return {'message': Messages.config_not_found}, 404
                else:
                    screen.config_id = screen_config_id            
            
            screen_group_id = request.values.get('group_id', screen.group_id)
            if screen_group_id:
                group = ScreenGroupModel.query.filter_by(id=screen_group_id, deleted=False).first()
                if not group:
                    return {'message': Messages.screengroup_not_found}, 404
                else:
                    screen.group_id = screen_group_id
            
            db.session.commit()
            screen.push_on_the_fly()
            return {'screen': screen.serialize()}, 200
        else:
            return {'message': Messages.screen_not_found}, 404

    @swagger.doc({
        'tags': ['screen'],
        'description': 'Delete screen',
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
                        'message': Messages.screen_not_found
                    }
                }
            }
        }
    })
    @token_required
    def delete(self, screen_id):
        screen = ScreenModel.query.filter_by(id=screen_id, deleted=False).first()
        if screen:
            screen.deleted = True
            db.session.commit()
            return {'screen': screen.serialize()}, 200
        else:
            return {'message': Messages.screen_not_found}, 404

class ScreenGroup(Resource):

    @swagger.doc({
        'tags': ['screengroup'],
        'description': 'Get all groups',
        'parameters': [
            {
                'name': 'onlyGroups',
                'required': False,
                'description': 'Returns an array of groups',
                'in': 'query',
                'type': 'boolean'
            }
        ],
        'responses': {
            '200': {
                'description': 'Groups list',
                'examples': {
                    'application/json': {
                        'groups': [ScreenGroupModel.doc()],
                        'no_group': [ScreenModel.doc()]
                    }
                }
            }
        }
    })
    @token_required
    def get(self):
        groups = ScreenGroupModel.query.filter_by(deleted=False).all()
        groups_list = [group.serialize() for group in groups]

        no_group_screens = ScreenModel.query.filter_by(group_id=None, deleted=False).all()
        no_group_screens_list = [screen.serialize() for screen in no_group_screens] 

        if request.values.get('onlyGroups', False):
            return groups_list
        else:
            return {
                        'groups': groups_list,
                        'no_group': no_group_screens_list
                    }, 200

    @swagger.doc({
        'tags': ['screengroup'],
        'description': 'Create a new group',
        'parameters': [
            {
                'name': 'name',
                'required': False,
                'description': 'Group name',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'location',
                'required': False,
                'description': 'Group location',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'active',
                'required': False,
                'description': 'If group is active or inactive',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'config_id',
                'required': False,
                'description': 'Configuration ID',
                'in': 'formData',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Group created',
                'examples': {
                    'application/json': {
                        'group': ScreenGroupModel.doc()
                    }
                }
            },
            '409': {
                'description': 'Group already exist',
                'examples': {
                    'application/json': {
                        'message': Messages.screengroup_already_exist
                    }
                }
            },
            '500': {
                'description': 'Error on item creation',
                'examples': {
                    'application/json': {
                        'message': Messages.database_add_error
                    }
                }
            }
        }
    })
    @token_required
    def post(self):
        name = request.values.get('name', str(uuid4()))
        location = request.values.get('location', None)
        active = str2bool(request.values.get('active', True))
        config_id = request.values.get('config_id', 1)

        if config_id:
            config = ConfigurationModel.query.filter_by(id=config_id, deleted=False).first()
            if not config:
                return {'message': Messages.config_not_found}, 404

        group = ScreenGroupModel.query.filter_by(name=name, deleted=False).first()
        if group:
            return {'message': Messages.screengroup_already_exist}, 409

        try:
            group = ScreenGroupModel(name=name, location=location, active=active)
            group.config_id = config_id
            db.session.add(group)
            db.session.commit()
            return {'group': group.serialize()}, 200
        except Exception as e:
            return {'message': Messages.database_add_error}, 500


class ScreenGroupItem(Resource):

    @swagger.doc({
        'tags': ['screengroup'],
        'description': 'Get group details and members',
        'parameters': [
            {
                'name': 'group_id',
                'required': True,
                'description': 'Group ID',
                'in': 'path',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Group',
                'examples': {
                    'application/json': {
                        'group': ScreenGroupModel.doc()
                    }
                }
            },
            '404': {
                'description': 'Group not found',
                'examples': {
                    'application/json': {
                        'message': Messages.screengroup_not_found
                    }
                }
            }
        }
    })
    @token_required
    def get(self, group_id):
        group = ScreenGroupModel.query.filter_by(id=group_id, deleted=False).first()
        if group:
            return {'group': group.serialize()}, 200
        else:
            return {'message': Messages.screengroup_not_found}, 404

    
    @swagger.doc({
        'tags': ['screengroup'],
        'description': 'Edit a group',
        'parameters': [
            {
                'name': 'group_id',
                'required': True,
                'description': 'Group ID',
                'in': 'path',
                'type': 'integer'
            },
            {
                'name': 'name',
                'required': False,
                'description': 'Group name',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'location',
                'required': False,
                'description': 'Group location',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'active',
                'required': False,
                'description': 'If group is active or inactive',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'config_id',
                'required': False,
                'description': 'Configuration ID',
                'in': 'formData',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Group modified',
                'examples': {
                    'application/json': {
                        'group': ScreenGroupModel.doc()
                    }
                }
            },
            '404': {
                'description': 'Group not found',
                'examples': {
                    'application/json': {
                        'message': Messages.screengroup_not_found
                    }
                }
            }
        }
    })
    @token_required    
    def put(self, group_id):
        group = ScreenGroupModel.query.filter_by(id=group_id, deleted=False).first()
        if group:
            group.name = request.values.get('name', group.name)
            group.location = request.values.get('location', group.location)
            group.active = str2bool(request.values.get('active', group.active))

            config_id = request.values.get('config_id', None)
            if config_id:
                config = ConfigurationModel.query.filter_by(id=config_id, deleted=False).first()
                if not config:
                    return {'message': Messages.config_not_found}, 404
                else:
                    group.config_id = config_id

            db.session.commit()
            group.push_on_the_fly()
            return {'group': group.serialize()}, 200
        else:
            return {'message': Messages.screengroup_not_found}, 404

    @swagger.doc({
        'tags': ['screengroup'],
        'description': 'Remove group',
        'parameters': [
            {
                'name': 'group_id',
                'required': True, 
                'description': 'Group ID',
                'in': 'path',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Group deleted',
                'examples': {
                    'application/json': {
                        'group': ScreenGroupModel.doc()
                    }
                }
            },
            '404': {
                'description': 'Group not found',
                'examples': {
                    'application/json': {
                        'message': Messages.screengroup_not_found
                    }
                }
            }
        }
    })
    @token_required
    def delete(self, group_id):
        group = ScreenGroupModel.query.filter_by(id=group_id, deleted=False).first()
        if group:
            group.deleted = True
            screens = ScreenModel.query.filter_by(group_id=group.id, deleted=False).all()
            for screen in screens:
                screen.active = False
                screen.group_id = None
            db.session.commit()
            return {'group': group.serialize()}, 200
        else:
            return {'message': Messages.screengroup_not_found}, 404

class ScreenGroupItemMember(Resource):

    @swagger.doc({
        'tags': ['screengroup'],
        'description': 'Add screen to group',
        'parameters': [
            {
                'name': 'group_id',
                'required': True,
                'description': 'Group ID',
                'in': 'path',
                'type': 'integer'
            },
            {
                'name': 'screen_id',
                'required': True,
                'description': 'Screen ID to add',
                'in': 'formData',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Screen added',
                'examples': {
                    'application/json': {
                        'screen': ScreenModel.doc(),
                        'group': ScreenGroupModel.doc()
                    }
                }
            },
            '400': {
                'description': 'Parameters error',
                'examples': {
                    'application/json': {
                        'message': '<error>'
                    }
                }
            },
            '404': {
                'description': 'Group or screen not found',
                'examples': {
                    'application/json': {
                        'message': Messages.screen_not_found
                    }
                }
            }
        }
    })
    @token_required
    def put(self, group_id):
        try:
            screen_id = request.values['screen_id']
        except Exception as e:
            return {'message': str(e)}, 400

        group = ScreenGroupModel.query.filter_by(id=group_id, deleted=False).first()
        if not group:
            return {'message': Messages.screengroup_not_found}, 404

        screen = ScreenModel.query.filter_by(id=screen_id, deleted=False).first()
        if screen:
            screen.group_id = group_id
            db.session.commit()
            return {
                        'screen': screen.serialize(),
                        'group': group.serialize()
                    }, 200
        else:
            return {'message': Messages.screen_not_found}, 404

    @swagger.doc({
        'tags': ['screengroup'],
        'description': 'Remove screen from group',
        'parameters': [
            {
                'name': 'group_id',
                'required': True,
                'description': 'Group ID',
                'in': 'path',
                'type': 'integer'
            },
            {
                'name': 'screen_id',
                'required': True,
                'description': 'Screen ID to add',
                'in': 'formData',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Screen removed',
                'examples': {
                    'application/json': {
                        'group': ScreenGroupModel.doc()
                    }
                }
            },
            '400': {
                'description': 'Parameters error',
                'examples': {
                    'application/json': {
                        'message': '<error>'
                    }
                }
            },
            '404': {
                'description': 'Group or screen not found',
                'examples': {
                    'application/json': {
                        'message': Messages.screen_not_found
                    }
                }
            }
        }
    })
    @token_required    
    def delete(self, group_id):
        try:
            screen_id = request.values['screen_id']
        except Exception as e:
            return {'message': str(e)}, 400

        group = ScreenGroupModel.query.filter_by(id=group_id, deleted=False).first()
        if not group:
            return {'message': Messages.screengroup_not_found}, 404

        screen = ScreenModel.query.filter_by(id=screen_id, group_id=group_id, deleted=False).first()
        if screen:
            screen.group_id = None
            db.session.commit()
            return {'group': group.serialize()}, 200
        else:
            return {'message': Messages.screen_not_found}, 404

class Configuration(Resource):
    @swagger.doc({
        'tags': ['configuration'],
        'description': 'Get all configurations',
        'parameters': [
            {
                'name': 'getArray',
                'required': False,
                'description': 'Return an array with all the configurations',
                'in': 'query',
                'type': 'boolean'
            }
        ],
        'responses': {
            '200': {
                'description': 'Configuration list',
                'examples': {
                    'application/json': {
                        'configurations': [
                            ConfigurationModel.doc()
                        ]
                    }
                }
            }
        }
    })
    @token_required
    def get(self):
        configurations = ConfigurationModel.query.filter_by(deleted=False).all()

        if len(configurations) == 0:
            dummyconf = ConfigurationModel()
            db.session.add(dummyconf)
            db.session.commit()
            configurations_list = [dummyconf]
        else:
            configurations_list = [conf.serialize() for conf in configurations]
        
        if str2bool(request.values.get('getArray', False)):
            return configurations_list, 200
        else:
            return {'configurations': configurations_list}, 200

    @swagger.doc({
        'tags': ['configuration'],
        'description': 'Add new configuration',
        'parameters': [
            {
                'name': 'description',
                'required': False,
                'description': 'Configuration description',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_active',
                'required': False,
                'description': 'Is head bar active?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'head_height',
                'required': False,
                'description': 'Height with measure unit',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_fontSize',
                'required': False,
                'description': 'Font size with measure unit',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_bgColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_textColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_borderColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_logo_active',
                'required': False,
                'description': '',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'head_logo_url',
                'required': False,
                'description': 'Head bar logo url',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_content_active',
                'required': False,
                'description': 'Has head bar text content?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'head_content_text',
                'required': False,
                'description': 'Head bar text',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_clock_active',
                'required': False,
                'description': 'Is clock in the head bar active?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'head_clock_textColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_clock_textColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_clock_bgColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_active',
                'required': False,
                'description': 'Is bottom bar active?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'bottom_content',
                'required': False,
                'description': 'Bottom bar text',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_marquee',
                'required': False,
                'description': 'Does bottom bar text scroll with marquee?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'bottom_height',
                'required': False,
                'description': 'Bottom bar height with measure unit',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_fontSize',
                'required': False,
                'description': 'Bottom bar font size with measure unit',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_bgColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_textColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'body_background_bgColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'body_background_bgImage',
                'required': False,
                'description': 'Image url',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'body_content_fixedContent',
                'required': False,
                'description': """"
                                    Fixed bars list.
                                    Example: [
                                                {
                                                    'active': true,
                                                    'bgColor': '#007EA7',
                                                    'textColor': '#fff',
                                                    'borderColor': '#fff',
                                                    'fontSize': '3em',
                                                    'marquee': false,
                                                    'content': 'Riunione ore 10 sala 210A'
                                                }
                                            ]
                                """,
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'body_content_columns',
                'required': False,
                'description': """"
                                    Columns list.
                                    Example: [
                                                {
                                                    'borderColor': '#fff',
                                                    'textColor': '#fff',
                                                    'html': 'bla bla'
                                                }
                                            ]
                                """,
                'in': 'formData',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'Configuration added',
                'examples': {
                    'application/json': {
                        'configuration': ConfigurationModel.doc()
                    }
                }
            },
            '500': {
                'description': 'Adding error',
                'examples': {
                    'application/json': {
                        'message': Messages.database_add_error
                    }
                }
            }
        }
    })
    @token_required
    def post(self):
        newconf = ConfigurationModel()
        newconf.description = request.values.get('description', newconf.description)
        newconf.head_active = str2bool(request.values.get('head_active', newconf.head_active))
        newconf.head_height = request.values.get('head_height', newconf.head_height)
        newconf.head_fontSize = request.values.get('head_fontSize', newconf.head_fontSize)
        newconf.head_bgColor = request.values.get('head_bgColor', newconf.head_bgColor)
        newconf.head_textColor = request.values.get('head_textColor', newconf.head_textColor)
        newconf.head_borderColor = request.values.get('head_borderColor', newconf.head_borderColor)
        newconf.head_logo_active = str2bool(request.values.get('head_logo_active', newconf.head_logo_active))
        newconf.head_logo_url = request.values.get('head_logo_url', newconf.head_logo_url)
        newconf.head_content_active = str2bool(request.values.get('head_content_active', newconf.head_content_active))
        newconf.head_content_text = request.values.get('head_content_text', newconf.head_content_text)
        newconf.head_clock_active = str2bool(request.values.get('head_clock_active', newconf.head_clock_active))
        newconf.head_clock_textColor = request.values.get('head_clock_textColor', newconf.head_clock_textColor)
        newconf.head_clock_bgColor = request.values.get('head_clock_bgColor', newconf.head_clock_bgColor)
        newconf.bottom_active = str2bool(request.values.get('bottom_active', newconf.bottom_active))
        newconf.bottom_content = request.values.get('bottom_content', newconf.bottom_content)
        newconf.bottom_marquee = str2bool(request.values.get('bottom_marquee', newconf.bottom_marquee))
        newconf.bottom_height = request.values.get('bottom_height', newconf.bottom_height)
        newconf.bottom_fontSize = request.values.get('bottom_fontSize', newconf.bottom_fontSize)
        newconf.bottom_bgColor = request.values.get('bottom_bgColor', newconf.bottom_bgColor)
        newconf.bottom_textColor = request.values.get('bottom_textColor', newconf.bottom_textColor)
        newconf.body_background_bgColor = request.values.get('body_background_bgColor', newconf.body_background_bgColor)
        newconf.body_background_bgImage = request.values.get('body_background_bgImage', newconf.body_background_bgImage)
        newconf.body_content_fixedContent = request.values.get('body_content_fixedContent', newconf.body_content_fixedContent)
        newconf.body_content_columns = request.values.get('body_content_columns', newconf.body_content_columns)

        try:
            db.session.add(newconf)
            db.session.commit()
            
            return {'configuration': newconf.serialize()}, 200
        
        except Exception as e:
            return {'message': Messages.database_add_error}, 500

class ConfigurationItem(Resource):
    @swagger.doc({
        'tags': ['configuration'],
        'description': 'Get specific configuration',
        'parameters': [
            {
                'name': 'conf_id',
                'required': True,
                'description': 'Configuration ID',
                'in': 'path',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Configuration',
                'examples': {
                    'application/json': {
                        'configuration': ConfigurationModel.doc()
                    }
                }
            },
            '404': {
                'description': 'Configuration not found',
                'examples': {
                    'application/json': {
                        'message': Messages.config_not_found
                    }
                }
            }
        }
    })
    @token_required
    def get(self, conf_id):
        conf = ConfigurationModel.query.filter_by(id=conf_id, deleted=False).first()
        if conf:
            return {'configuration': conf.serialize()}, 200
        else:
            return {'message': Messages.config_not_found}, 404

    @swagger.doc({
        'tags': ['configuration'],
        'description': 'Edit configuration',
        'parameters': [
            {
                'name': 'description',
                'required': False,
                'description': 'Configuration description',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_active',
                'required': False,
                'description': 'Is head bar active?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'head_height',
                'required': False,
                'description': 'Height with measure unit',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_fontSize',
                'required': False,
                'description': 'Font size with measure unit',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_bgColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_textColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_borderColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_logo_active',
                'required': False,
                'description': '',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'head_logo_url',
                'required': False,
                'description': 'Head bar logo url',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_content_active',
                'required': False,
                'description': 'Has head bar text content?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'head_content_text',
                'required': False,
                'description': 'Head bar text',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_clock_active',
                'required': False,
                'description': 'Is clock in the head bar active?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'head_clock_textColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_clock_textColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'head_clock_bgColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_active',
                'required': False,
                'description': 'Is bottom bar active?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'bottom_content',
                'required': False,
                'description': 'Bottom bar text',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_marquee',
                'required': False,
                'description': 'Does bottom bar text scroll with marquee?',
                'in': 'formData',
                'type': 'boolean'
            },
            {
                'name': 'bottom_height',
                'required': False,
                'description': 'Bottom bar height with measure unit',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_fontSize',
                'required': False,
                'description': 'Bottom bar font size with measure unit',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_bgColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'bottom_textColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'body_background_bgColor',
                'required': False,
                'description': 'Hex or rgb() color',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'body_background_bgImage',
                'required': False,
                'description': 'Image url',
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'body_content_fixedContent',
                'required': False,
                'description': """"
                                    Fixed bars list.
                                    Example: [
                                                {
                                                    'active': true,
                                                    'bgColor': '#007EA7',
                                                    'textColor': '#fff',
                                                    'borderColor': '#fff',
                                                    'fontSize': '3em',
                                                    'marquee': false,
                                                    'content': 'Riunione ore 10 sala 210A'
                                                }
                                            ]
                                """,
                'in': 'formData',
                'type': 'string'
            },
            {
                'name': 'body_content_columns',
                'required': False,
                'description': """"
                                    Columns list.
                                    Example: [
                                                {
                                                    'borderColor': '#fff',
                                                    'textColor': '#fff',
                                                    'html': 'bla bla'
                                                }
                                            ]
                                """,
                'in': 'formData',
                'type': 'string'
            }
        ],
        'responses': {
            '200': {
                'description': 'Configuration added',
                'examples': {
                    'application/json': {
                        'configuration': ConfigurationModel.doc()
                    }
                }
            },
            '404': {
                'description': 'Configuration not found',
                'examples': {
                    'application/json': {
                        'message': Messages.config_not_found
                    }
                }
            },
            '500': {
                'description': 'Update error',
                'examples': {
                    'application/json': {
                        'message': Messages.database_update_error
                    }
                }
            }
        }
    })
    @token_required
    def put(self, conf_id):
        conf = ConfigurationModel.query.filter_by(id=conf_id, deleted=False).first()
        if not conf:
            return {'message': Messages.config_not_found}, 404
        
        conf.description = request.values.get('description', conf.description)
        conf.head_active = str2bool(request.values.get('head_active', conf.head_active))
        conf.head_height = request.values.get('head_height', conf.head_height)
        conf.head_fontSize = request.values.get('head_fontSize', conf.head_fontSize)
        conf.head_bgColor = request.values.get('head_bgColor', conf.head_bgColor)
        conf.head_textColor = request.values.get('head_textColor', conf.head_textColor)
        conf.head_borderColor = request.values.get('head_borderColor', conf.head_borderColor)
        conf.head_logo_active = str2bool(request.values.get('head_logo_active', conf.head_logo_active))
        conf.head_logo_url = request.values.get('head_logo_url', conf.head_logo_url)
        conf.head_content_active = str2bool(request.values.get('head_content_active', conf.head_content_active))
        conf.head_content_text = request.values.get('head_content_text', conf.head_content_text)
        conf.head_clock_active = str2bool(request.values.get('head_clock_active', conf.head_clock_active))
        conf.head_clock_textColor = request.values.get('head_clock_textColor', conf.head_clock_textColor)
        conf.head_clock_bgColor = request.values.get('head_clock_bgColor', conf.head_clock_bgColor)
        conf.bottom_active = str2bool(request.values.get('bottom_active', conf.bottom_active))
        conf.bottom_content = request.values.get('bottom_content', conf.bottom_content)
        conf.bottom_marquee = str2bool(request.values.get('bottom_marquee', conf.bottom_marquee))
        conf.bottom_height = request.values.get('bottom_height', conf.bottom_height)
        conf.bottom_fontSize = request.values.get('bottom_fontSize', conf.bottom_fontSize)
        conf.bottom_bgColor = request.values.get('bottom_bgColor', conf.bottom_bgColor)
        conf.bottom_textColor = request.values.get('bottom_textColor', conf.bottom_textColor)
        conf.body_background_bgColor = request.values.get('body_background_bgColor', conf.body_background_bgColor)
        conf.body_background_bgImage = request.values.get('body_background_bgImage', conf.body_background_bgImage)
        conf.body_content_fixedContent = request.values.get('body_content_fixedContent', conf.body_content_fixedContent)
        conf.body_content_columns = request.values.get('body_content_columns', conf.body_content_columns)

        #Update all screens
        screens = ScreenModel.query.filter_by(config_id=conf.id, deleted=False).all()
        for screen in screens:
            screen.config_v = screen.config_v + 1
        
        groups = ScreenGroupModel.query.filter_by(config_id=conf.id, deleted=False).all()
        for group in groups:
            group.config_v = group.config_v + 1

        try:
            db.session.commit()
            
            return {'configuration': conf.serialize()}, 200
        
        except Exception as e:
            log.error(str(e))
            return {'message': Messages.database_update_error}, 500


    @swagger.doc({
        'tags': ['configuration'],
        'description': 'Delete specific configuration',
        'parameters': [
            {
                'name': 'conf_id',
                'required': True,
                'description': 'Configuration ID',
                'in': 'path',
                'type': 'integer'
            }
        ],
        'responses': {
            '200': {
                'description': 'Configuration deleted',
                'examples': {
                    'application/json': {
                        'configuration': ConfigurationModel.doc(deleted=True)
                    }
                }
            },
            '404': {
                'description': 'Configuration not found',
                'examples': {
                    'application/json': {
                        'message': Messages.config_not_found
                    }
                }
            },
            '500': {
                'description': 'Error on deleting configuration',
                'examples': {
                    'application/json': {
                        'error': Messages.database_update_error
                    }
                }
            }
        }
    })
    @token_required
    def delete(self, conf_id):
        conf = ConfigurationModel.query.filter_by(id=conf_id, deleted=False).first()
        if not conf:
            return {'message': Messages.config_not_found}, 404

        conf.deleted = True

        try:
            db.session.commit()
            return {'configuration': conf.serialize()}, 200
        
        except Exception as e:
            return {'message': Messages.database_update_error}, 500        


api.add_resource(Version, '/version')
api.add_resource(Auth, '/auth')
api.add_resource(Screen, '/screens')
api.add_resource(ScreenItem, '/screen/<int:screen_id>')
api.add_resource(ScreenGroup, '/groups')
api.add_resource(ScreenGroupItem, '/group/<int:group_id>')
api.add_resource(ScreenGroupItemMember, '/group/<int:group_id>/member')
api.add_resource(Configuration, '/configurations')
api.add_resource(ConfigurationItem, '/configuration/<int:conf_id>')