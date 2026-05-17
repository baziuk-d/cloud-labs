from flask import jsonify
from store.dao.user_dao import UserDAO
from store.service.user_service import UserService
import requests
import os


class AuthService:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    def signup(self, request_model, user_service: UserService):
        try:
            response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={os.getenv('IDENTITY_KEY')}",
                headers={"Content-Type": "application/json"},
                json=request_model.json
            )
        except Exception:
            print("Response text:", response.text)
            raise
        data = request_model.json
        email = data['email']
        name = data.get('name', '')

        user_service.insert_user(username=name, email=email)
        return {"message": "User registered successfully"}
    
    def login(self, request_model):
        try:
            response = requests.post(
                f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.getenv('IDENTITY_KEY')}",
                headers={"Content-Type": "application/json"},
                json=request_model.json
            )
        except Exception:
            print("Response text:", response.text)
            raise
        data = response.json()
        id_token = data.get('idToken')
        return jsonify({'idToken': id_token}), response.status_code
