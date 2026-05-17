from flask import request, jsonify
from functools import wraps
import os
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401

        token = auth_header.split(' ')[1]
        CLIENT_ID = os.getenv('PROJECT_ID')
        try:
            decoded_token = id_token.verify_firebase_token(
                token,
                google_requests.Request(),
                CLIENT_ID
            )
            # Optionally, you can attach decoded_token to request context here
        except Exception as e:
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401

        return f(*args, **kwargs)
    return decorated

# ...existing code...
