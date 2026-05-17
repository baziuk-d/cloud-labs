# dao/table_dao.py

class TableDAO:
    def __init__(self, db):
        self.db = db

    def create_and_distribute_data(self, parent_table, new_table1, new_table2):
        """Виклик процедури CreateAndDistributeData"""
        try:
            cursor = self.db.cursor()
            # Виклик процедури
            cursor.callproc('CreateAndDistributeData', (parent_table, new_table1, new_table2))
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
        finally:
            cursor.close()
