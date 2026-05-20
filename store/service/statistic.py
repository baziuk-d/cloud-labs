# service/statistic_service.py

class StatisticService:
    def __init__(self, statistic_dao):
        self.statistic_dao = statistic_dao

    def get_statistic(self, stat_type):
        """Отримання статистики через DAO"""
        return self.statistic_dao.call_statistic_function(stat_type)
