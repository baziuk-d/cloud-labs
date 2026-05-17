class UserDTO:
    def __init__(self, user_id, name, email,):
        self.user_id = user_id
        self.name = name
        self.email = email
        

    def to_dict(self):
        return {
            'id': self.user_id,
            'name': self.name,
            'email': self.email,
            
        }

        
class CourseDTO:
    def __init__(self, course_id, title, description):
        self.course_id = course_id
        self.title = title
        self.description = description

    def to_dict(self):
        return {
            'id': self.course_id,
            'title': self.title,
            'description': self.description
        }


class ProgressDTO:
    def __init__(self, module_title, status):
        self.module_title = module_title
        self.status = status

    def to_dict(self):
        return {
            'module_title': self.module_title,
            'status': self.status
        }
