class TableService:
    def __init__(self, table_dao):
        self.table_dao = table_dao

    def create_and_distribute_data(self, parent_table, new_table1, new_table2):
        """Бізнес-логіка для виклику DAO"""
        self.table_dao.create_and_distribute_data(parent_table, new_table1, new_table2)