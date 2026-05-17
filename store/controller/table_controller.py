# controllers/table_controller.py

from flask import Blueprint, request, jsonify
from store.dao.table_dao import TableDAO
from store.service.table import TableService
from store.db.connection import db_connection as db

table_bp = Blueprint('table', __name__)


table_dao = TableDAO(db)
table_service = TableService(table_dao)

@table_bp.route('/tables/distribute', methods=['POST'])
def distribute_data():
    data = request.get_json()

    if not all(key in data for key in ('parent_table', 'new_table1', 'new_table2')):
        return jsonify({'error': 'Missing required fields: parent_table, new_table1, new_table2'}), 400

    parent_table = data['parent_table']
    new_table1 = data['new_table1']
    new_table2 = data['new_table2']

    try:
        # Виклик сервісу
        table_service.create_and_distribute_data(parent_table, new_table1, new_table2)
        return jsonify({'message': 'Data distributed successfully!'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
