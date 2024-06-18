from sqlite_orm.columns.column import Column


class IntegerField(Column):
    _value: int | None

    _type = 'INTEGER'

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._value: int | None = None

    def set_value(
            self,
            value: int,
    ):
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def sql_value(self):
        return self._value

    def __str__(self):
        return self._type
