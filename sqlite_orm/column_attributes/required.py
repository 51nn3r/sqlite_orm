from sqlite_orm.column_attributes.column_attribute import ColumnAttribute


class Required(ColumnAttribute):
    def __str__(self):
        return 'NOT NULL'


REQUIRED: Required = Required()
