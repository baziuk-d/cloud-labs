from store.dao.user_dao import UserDAO
from collections import defaultdict


class UserService:
    def __init__(self, user_dao: UserDAO):
        self.user_dao = user_dao

    def get_all_users(self):
        """Retrieve all users from the database."""
        return self.user_dao.get_all_users()

    def insert_user(self, username, email):
        """Insert a new user into the database."""
        return self.user_dao.insert_user(username, email)

    def get_user_by_id(self, user_id):
        """Retrieve a user by their ID."""
        return self.user_dao.get_user_by_id(user_id)
    
    def get_user_by_name(self, name):
        """Retrieve a user by their name."""
        return self.user_dao.get_user_by_name(name)

    def update_user(self, user_id, name=None, email=None, password=None):
        return self.user_dao.update_user(user_id, name=name, email=email, password=password)

    def delete_user(self, user_id):
        """Delete a user from the database."""
        return self.user_dao.delete_user(user_id)

    def get_user_courses(self, user_id):
        """Retrieve all courses associated with a specific user."""
        return self.user_dao.get_user_courses(user_id)

    def get_user_progress(self, user_id):
        """Retrieve the progress of a user across their enrolled modules."""
        return self.user_dao.get_user_progress(user_id)

    def get_all_users_with_courses(self):
        data = self.user_dao.get_all_users_with_courses()
        users_dict = defaultdict(lambda: {'id': None, 'username': None, 'email': None, 'courses': []})

        for row in data:
            user_id, username, email, course_id, course_name, course_description = row
            
            # Initialize user details if not already done
            if users_dict[user_id]['id'] is None:
                users_dict[user_id].update({
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'courses': []
                })

            # If the user has an associated course, add it to their course list
            if course_id:
                users_dict[user_id]['courses'].append({
                    'id': course_id,
                    'name': course_name,
                    'description': course_description
                })

        # Convert to a list for JSON serialization
        return list(users_dict.values())
    
    def insert_noname_records(self):
        """Виклик процедури через DAO"""
        self.user_dao.call_insert_noname_records_procedure()
