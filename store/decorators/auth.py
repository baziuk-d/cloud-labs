from flask import request, jsonify
from functools import wraps
import os
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials

if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
        'projectId': os.getenv('PROJECT_ID')
    })


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401

        token = auth_header.split(' ')[1]
        try:
            firebase_auth.verify_id_token(token)
        except Exception as e:
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401

        return f(*args, **kwargs)
    return decorated
