class EnrollmentDAO:
    def __init__(self, db):
        self.db = db

    def get_all_enrollments(self):
        cursor = self.db.cursor()
        sql = """
            SELECT 
                enrollments.id, 
                users.name AS username,
                courses.title AS course_name, 
                enrollments.enrollment_date, 
                enrollments.completion_status 
            FROM enrollments
            JOIN users ON enrollments.user_id = users.id
            JOIN courses ON enrollments.course_id = courses.id
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result


    def add_enrollment(self, user_id, course_id, completion_status):
        sql = """
            INSERT INTO enrollments (user_id, course_id, enrollment_date, completion_status)
            VALUES (%s, %s, NOW(), %s)
        """
        cursor = self.db.cursor()
        cursor.execute(sql, (user_id, course_id, completion_status))
        self.db.commit()

    def delete_enrollment(self, enrollment_id):
        sql = "DELETE FROM enrollments WHERE id = %s"
        cursor = self.db.cursor()
        cursor.execute(sql, (enrollment_id,))
        self.db.commit()
    
    def add_enrollment_by_names(self, user_name, course_title, enrollment_date, completion_status):
        try:
            cursor = self.db.cursor()
            cursor.callproc('InsertEnrollmentByNames', (user_name, course_title, enrollment_date, completion_status))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            cursor.close()
    