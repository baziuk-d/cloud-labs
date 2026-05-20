from flask import Blueprint, request, jsonify
from store.dao.review import ReviewDAO
from store.db.connection import db_connection as db
review_bp = Blueprint('review', __name__)


review_dao = ReviewDAO(db)

@review_bp.route('/reviews', methods=['POST'])
def insert_review():
    
    data = request.get_json()

    # Перевірка обов'язкових полів
    if not all(key in data for key in ('course_id', 'user_id', 'rating', 'comment')):
        return jsonify({'error': 'Missing required fields: course_id, user_id, rating, comment'}), 400

    course_id = data['course_id']
    user_id = data['user_id']
    rating = data['rating']
    comment = data['comment']

    try:
        review_dao.call_insert_review_procedure(course_id, user_id, rating, comment)
        return jsonify({'message': 'Review inserted successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
