from flask import Flask
FLASK_DEBUG=1
app = Flask(__name__)
from app import controller

from flask_swagger_ui import get_swaggerui_blueprint
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGER_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app-name' : "Pharmagenda"
    }
)
app.register_blueprint(SWAGGER_BLUEPRINT,url_prefix=SWAGGER_URL)