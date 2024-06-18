from sqlite_orm.columns.column import Column


class BooleanField(Column):
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
            value: int | bool,
    ):
        if isinstance(value, bool):
            self._value = 1
        else:
            self._value = value

    @property
    def value(self):
        return bool(self._value)

    @property
    def sql_value(self):
        return self._value

    def __str__(self):
        return self._type
