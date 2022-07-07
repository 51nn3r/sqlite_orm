class PrimaryKey:
    def __str__(self):
        return 'PRIMARY KEY'


class Default:
    def __init__(self, default=None):
        self.default_value = default

    def __str__(self):
        return f'DEFAULT {self.default_value}'


class Required:
    def __str__(self):
        return 'NOT NULL'


class ForeignKey:
    column_name = None

    def __init__(self, foreign_key=None, ondelete=None):
        self.key_destination = foreign_key
        self.ondelete = ondelete

    def __str__(self):
        destination_table = self.key_destination.split('.')[0]
        destination_column = self.key_destination.split('.')[1]
        string = f'FOREIGN KEY ({self.column_name}) REFERENCES {destination_table}({destination_column})'
        if self.ondelete is not None:
            string += f' ON DELETE {self.ondelete}'
        return string
