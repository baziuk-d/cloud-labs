from flask import request, jsonify
from functools import wraps
import os
import requests as http_requests


def verify_token(token):
    api_key = os.getenv('IDENTITY_KEY')
    response = http_requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}",
        json={"idToken": token},
        timeout=5
    )
    if response.status_code != 200:
        raise Exception(response.json().get('error', {}).get('message', 'Invalid token'))
    return response.json()


def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', None)
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Authorization header missing or invalid'}), 401

        token = auth_header.split(' ')[1]
        try:
            verify_token(token)
        except Exception as e:
            return jsonify({'error': 'Invalid token', 'details': str(e)}), 401

        return f(*args, **kwargs)
    return decorated
