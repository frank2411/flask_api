import os
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS

from .models import db
from .api import api_blueprint


load_dotenv()


def create_app(testing=False):
    app = Flask('work_api')

    config_path = os.getenv("WORK_API_CONFIG_PATH", "work_api.config.LocalConfig")
    app.config.from_object(config_path)

    if testing is True:
        app.config['TESTING'] = True

    CORS(app)

    # Init db extension
    db.init_app(app)

    app.register_blueprint(api_blueprint)
    return app
