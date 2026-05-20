# controllers/statistic_controller.py

from flask import Blueprint, jsonify, request
from store.dao.statistic import StatisticDAO
from store.service.statistic import StatisticService
from store.db.connection import db_connection as db

statistic_bp = Blueprint('statistic', __name__)


statistic_dao = StatisticDAO(db)
statistic_service = StatisticService(statistic_dao)

@statistic_bp.route('/statistics', methods=['GET'])
def get_statistic():
    """Отримати статистику через процедуру CallStatisticFunction"""
    stat_type = request.args.get('type')
    if stat_type not in ('MAX', 'MIN', 'SUM', 'AVG'):
        return jsonify({'error': 'Invalid statType. Use MAX, MIN, SUM, or AVG.'}), 400

    try:
        # Виклик сервісу для отримання статистики
        result = statistic_service.get_statistic(stat_type)
        return jsonify({'StatisticResult': result[0][0]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
