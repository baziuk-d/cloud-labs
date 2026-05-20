import pymysql
from store.db.connection import get_db_connection


class UserDAO:
    def __init__(self, db=None):
        self.db = db
        self.use_pool = db is None

    def _get_connection(self):
        """Get a database connection from the pool if needed"""
        if self.use_pool:
            return get_db_connection()
        return self.db

    def get_all_users(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "SELECT id, name, email FROM users"  
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        if self.use_pool:
            conn.close()
        return users

    def get_user_by_id(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "SELECT id, name, email FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        cursor.close()
        if self.use_pool:
            conn.close()
        return user
    
    def get_user_by_name(self, name):
        conn = self._get_connection()
        cursor = conn.cursor()
        query = "SELECT id, name, email FROM users WHERE name = %s"
        cursor.execute(query, (name,))
        user = cursor.fetchone()
        cursor.close()
        if self.use_pool:
            conn.close()
        return user

    def insert_user(self, name, email):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "INSERT INTO users (name, email) VALUES (%s, %s)"
            cursor.execute(query, (name, email))
            conn.commit()
            cursor.close()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            if self.use_pool:
                conn.close()

    def update_user(self, user_id, name=None, email=None, password=None):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "UPDATE users SET "
            fields = []
            values = []

            if name:
                fields.append("name = %s")
                values.append(name)

            if email:
                fields.append("email = %s")
                values.append(email)

            if password:
                fields.append("password = %s")
                values.append(password)

            if fields:
                query += ", ".join(fields) + " WHERE id = %s"
                values.append(user_id)
                cursor.execute(query, tuple(values))
                conn.commit()
            cursor.close()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            if self.use_pool:
                conn.close()

    def delete_user(self, user_id):
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            query = "DELETE FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            conn.commit()
            cursor.close()
            return {'message': 'User deleted successfully!'}, 204
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            if self.use_pool:
                conn.close()

    def get_user_courses(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        query = ("""
            SELECT courses.id, courses.title, courses.description
            FROM enrollments
            JOIN courses ON enrollments.course_id = courses.id
            WHERE enrollments.user_id = %s
        """)
        cursor.execute(query, (user_id,))
        courses = cursor.fetchall()
        cursor.close()
        if self.use_pool:
            conn.close()
        return courses
    
    def get_all_users_with_courses(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        sql = """
           SELECT users.id AS user_id, users.name, users.email,
            courses.id AS course_id, courses.title AS course_name, courses.description
            FROM users
            LEFT JOIN enrollments ON users.id = enrollments.user_id
            LEFT JOIN courses ON enrollments.course_id = courses.id
            ORDER BY users.id
        """
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
        except pymysql.err.OperationalError as e:
            print(f"Error occurred: {e}")
            cursor.close()
            if self.use_pool:
                conn.close()
            raise
        cursor.close()
        if self.use_pool:
            conn.close()
        return data

    def get_user_progress(self, user_id):
        conn = self._get_connection()
        cursor = conn.cursor()
        query = ("""
            SELECT modules.title, progress.status
            FROM progress
            JOIN modules ON progress.module_id = modules.id
            WHERE progress.user_id = %s
        """)
        cursor.execute(query, (user_id,))
        progress = cursor.fetchall()
        cursor.close()
        if self.use_pool:
            conn.close()
        return progress
    
    def call_insert_noname_records_procedure(self):
        """Виклик процедури InsertNonameRecords"""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.callproc('InsertNonameRecords')
            conn.commit()
            cursor.close()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            if self.use_pool:
                conn.close()
