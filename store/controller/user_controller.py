
from flask import Blueprint, request, jsonify
from store.dao.user_dao import UserDAO
from store.dto.user_dto import UserDTO, CourseDTO, ProgressDTO
from store.service.user_service import UserService
from store.service.auth import AuthService


user_bp = Blueprint('user', __name__)


# Initialize the User DAO and Service
user_dao = UserDAO()
user_service = UserService(user_dao)



@user_bp.route('/users', methods=['GET'])
def get_users():
    users = user_service.get_all_users()
    user_dtos = [UserDTO(user[0], user[1], user[2]).to_dict() for user in users]    
    return jsonify(user_dtos), 200

@user_bp.route('/signup', methods=['POST'])
def create_user(request=request):
    data = request
    auth_service = AuthService(user_dao)
    user = auth_service.signup(data, user_service)
    return jsonify({'message': 'User created successfully!'})

@user_bp.route('/login', methods=['POST'])
def login_user(request=request):
    data = request
    auth_service = AuthService(user_dao)
    response = auth_service.login(data)
    return response

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = user_service.get_user_by_id(user_id)
    if user:
        user_dto = UserDTO(user[0], user[1], user[2]).to_dict()
        return jsonify(user_dto), 200
    return jsonify({'message': 'User not found'}), 404

@user_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    username = data.get('name')
    email = data.get('email')   
    password = data.get('password')

    user_service.update_user(user_id, name=username, email=email, password=password)
    return jsonify({'message': 'User updated successfully!'}), 200

@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    response, status_code = user_service.delete_user(user_id)
    return jsonify(response), status_code

@user_bp.route('/users/<int:user_id>/courses', methods=['GET'])
def get_user_courses(user_id):
    courses = user_service.get_user_courses(user_id)
    course_dtos = [CourseDTO(course[0], course[1], course[2]).to_dict() for course in courses]
    return jsonify(course_dtos), 200

@user_bp.route('/users/courses', methods=['GET'])
def get_all_users_with_courses():
    users_with_courses = user_service.get_all_users_with_courses()
    return jsonify(users_with_courses), 200

@user_bp.route('/users/<int:user_id>/progress', methods=['GET'])
def get_user_progress(user_id):
    progress = user_service.get_user_progress(user_id)
    progress_dtos = [ProgressDTO(module[0], module[1]).to_dict() for module in progress]
    return jsonify(progress_dtos), 200


@user_bp.route('/users/noname', methods=['POST'])
def insert_noname_users():
    """Виклик процедури InsertNonameRecords"""
    try:
        user_service.insert_noname_records()
        return jsonify({'message': 'Noname records inserted successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500



