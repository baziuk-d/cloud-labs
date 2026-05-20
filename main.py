import os
from flask import Flask, jsonify
from store.route import init_routes
from store.db.connection import db_connection
from flask import request
from store.decorators.auth import require_auth
from flask_swagger_ui import get_swaggerui_blueprint
app = Flask(__name__)


SWAGGER_URL = "/apidocs"
API_URL = "/static/openapi.json"  

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Flask API with OpenAPI 3.0 and Bearer"}
)
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/_health', methods=['GET'])
def health_check():
    """Simple health check that doesn't require database"""
    return jsonify({"status": "healthy"}), 200


init_routes(app)


@app.before_request
def global_auth():
    if request.path.startswith('/apidocs') or request.path.startswith('/static'):
        return
    exempt_endpoints = ['user.login_user',
                        'user.create_user',
                        'apispec_1',
                        'apidocs'
                        ]
    if request.endpoint in exempt_endpoints:
        return
    result = require_auth(lambda: None)()
    if result is not None:
        return result


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
