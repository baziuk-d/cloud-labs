class StatisticDAO:
    def __init__(self, db):
        self.db = db

    def call_statistic_function(self, stat_type):
        """Виклик процедури CallStatisticFunction"""
        try:
            cursor = self.db.cursor()
            # Виклик збереженої процедури
            cursor.callproc('CallStatisticFunction', (stat_type,))
            result = cursor.fetchall()
            cursor.close()
            return result
        except Exception as e:
            raise e
