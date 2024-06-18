from sqlite_orm.columns.column import Column


class FloatField(Column):
    _value: float | None

    _type = 'FLOAT'

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._value: float | None = None

    def set_value(
            self,
            value: float,
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
