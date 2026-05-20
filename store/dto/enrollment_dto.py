# enrollment_dto.py

class EnrollmentDTO:
    def __init__(self, enrollment_id, username, course_name, enrollment_date, completion_status):
        self.enrollment_id = enrollment_id
        self.username = username          
        self.course_name = course_name    
        self.enrollment_date = enrollment_date
        self.completion_status = completion_status

    def to_dict(self):
        return {
            'id': self.enrollment_id,
            'username': self.username,                
            'course_name': self.course_name,          
            'enrollment_date': self.enrollment_date,
            'completion_status': self.completion_status
        }
