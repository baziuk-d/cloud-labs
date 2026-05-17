# models/review_dto.py
class ReviewDTO:
    def __init__(self, course_id, user_id, rating, comment):
        self.course_id = course_id
        self.user_id = user_id
        self.rating = rating
        self.comment = comment
