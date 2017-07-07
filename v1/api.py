from flask import Blueprint, render_template, request, session, url_for, redirect, jsonify
from flask_restful_swagger_2 import Api, Resource, swagger

import v1.engine

#Logging
import logging
import util.logger

apiVersion = '1.0'

app = Blueprint('apiv1', __name__)
api = Api(app, api_version=apiVersion, base_path='/api/v1', api_spec_url='/spec')

@app.route('/docs')
def render_docs():
    logging.info('Rendering api docs')
    return """
<!DOCTYPE html>
<html>
  <head>
    <title>API Docs</title>
    <!-- needed for adaptive design -->
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!--
    ReDoc doesn't change outer page styles
    -->
    <style>
      body {
        margin: 0;
        padding: 0;
      }
    </style>
  </head>
  <body>
    <redoc spec-url='spec.json'></redoc>
    <script src="https://rebilly.github.io/ReDoc/releases/latest/redoc.min.js"> </script>
  </body>
</html>
"""


class Version(Resource):
    @swagger.doc({
        'tags': ['api'],
        'description': 'Return info about this api and its engine',
        'responses': {
            '200': {
                'description': 'Versions',
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
        session['test'] = 'ok'
        return {
                'engine_version': v1.engine.engine_version,
                'api_version': apiVersion,
                'cookies': str(request.cookies)
                }
api.add_resource(Version, '/version')