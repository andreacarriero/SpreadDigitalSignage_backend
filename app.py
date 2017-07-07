from flask import Flask
from flask_cors import CORS, cross_origin

#MODULES
from db import db

app = Flask(__name__)
#Cross Origin
CORS(app, resources={r"/api/*": {"origins": "*"}})

#STATIC CONFING
##DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
##SESSION
app.secret_key = '@4f<\x1e\x9et\x99b"b\xca\x8cV\xa8\xb92\x03\x96\xf3I\xf0\xf7\xd7\xf0\xdaR5w\x93'
##DEV
app.config['TEMPLATES_AUTO_RELOAD'] = True

#ROUTER
import v1.api
app.register_blueprint(v1.api.app, url_prefix='/api/v1')



#RUN
db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)