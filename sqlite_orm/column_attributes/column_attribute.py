class ColumnAttribute:
    def __eq__(self, other):
        return self.__class__ == other.__class__

    def __str__(self):
        return 'COLUMN_ATTRIBUTE'
