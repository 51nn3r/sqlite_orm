from sqlite_orm.columns.column import Column


class StringField(Column):
    _value: str | None

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._value: str | None = None

    def set_value(
            self,
            value: str,
    ):
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def sql_value(self):
        return self._value

    def __str__(self):
        return 'TEXT'
