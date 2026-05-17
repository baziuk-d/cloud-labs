from store.dto.enrollment_dto import EnrollmentDTO


class EnrollmentService:
    def __init__(self, enrollment_dao):  # Приймаємо enrollment_dao як параметр
        self.enrollment_dao = enrollment_dao

    def get_all_enrollments(self):
        enrollments = self.enrollment_dao.get_all_enrollments()
        return [
            EnrollmentDTO(
                enrollment[0], 
                enrollment[1], 
                enrollment[2], 
                enrollment[3], 
                enrollment[4]  
            ).to_dict() for enrollment in enrollments
        ]

    def add_enrollment(self, user_id, course_id, completion_status):
        self.enrollment_dao.add_enrollment(user_id, course_id, completion_status)

    def delete_enrollment(self, enrollment_id):
        self.enrollment_dao.delete_enrollment(enrollment_id)
        
    def add_enrollment_by_names(self, user_name, course_title, enrollment_date, completion_status):
        self.enrollment_dao.add_enrollment_by_names(user_name, course_title, enrollment_date, completion_status)
