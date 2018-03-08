from flask import Flask
from flask_cors import CORS, cross_origin

from util.configuration_loader import conf

#MODULES
from util.db import db
import util.logger
from util.redissession import RedisSessionInterface

app = Flask(__name__)
##Cross Origin
CORS(app, resources={r"/api/*": {"origins": "*"}})
##Session
#app.session_interface = RedisSessionInterface()

#STATIC CONFING
##DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = conf['databaseURI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
##SESSION
app.secret_key = conf['secretKey']
##DEV
app.config['TEMPLATES_AUTO_RELOAD'] = True

##ROUTER
import v1.api
app.register_blueprint(v1.api.app, url_prefix='/api/v1')



##RUN
db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)