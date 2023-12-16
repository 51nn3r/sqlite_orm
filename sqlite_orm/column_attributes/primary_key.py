from sqlite_orm.column_attributes.column_attribute import ColumnAttribute


class PrimaryKey(ColumnAttribute):
    def __str__(self):
        return 'PRIMARY KEY'


PRIMARY_KEY: PrimaryKey = PrimaryKey()
