from sqlite_orm.column_attributes.column_attribute import ColumnAttribute


class Default(ColumnAttribute):
    def __init__(self, default=None):
        self.default_value = default

    def __str__(self):
        return f'DEFAULT {self.default_value}'


DEFAULT: Default = Default()
