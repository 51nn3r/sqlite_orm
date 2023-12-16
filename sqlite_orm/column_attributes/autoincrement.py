from sqlite_orm.column_attributes.column_attribute import ColumnAttribute


class Autoincrement(ColumnAttribute):
    def __str__(self):
        return 'AUTOINCREMENT'


AUTOINCREMENT: Autoincrement = Autoincrement()
