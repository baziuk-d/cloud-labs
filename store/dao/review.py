class ReviewDAO:
    def __init__(self, db):
        self.db = db

    def call_insert_review_procedure(self, course_id, user_id, rating, comment):
        """Виклик збереженої процедури InsertIntoReviews."""
        try:
            cursor = self.db.cursor()
            cursor.callproc('InsertIntoReviews', (course_id, user_id, rating, comment))
            self.db.commit()
            cursor.close()
        except Exception as e:
            self.db.rollback()
            raise e
