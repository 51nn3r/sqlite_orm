from sqlite_orm.column_attributes.column_attribute import ColumnAttribute


class NotNull(ColumnAttribute):
    def __str__(self):
        return 'NOT NULL'


NOT_NULL: NotNull = NotNull()
