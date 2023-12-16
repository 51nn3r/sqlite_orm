from typing import Optional

from sqlite_orm.columns.column import Column

from sqlite_orm.settings import SQLITE_TYPES


class ForeignKey(Column):
    _model: type
    _bound_model: Optional
    _related_name: str
    _value: Optional
    _ondelete: str | None

    def __init__(
            self,
            model,
            related_name=None,
            ondelete=None,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._model = model
        self._bound_model = None
        self._related_name = related_name
        self._ondelete = ondelete
        self._value: Optional = None

    def set_value(
            self,
            value: Optional,
    ):
        if type(value) in SQLITE_TYPES:
            kwargs = {self._model().primary_key.name: value}
            self._value = self._model(**kwargs)
        else:
            self._value = value

    def set_bound_model(
            self,
            model: type,
    ):
        self._bound_model = model

    @property
    def bound_model(self) -> Optional:
        return self._bound_model

    @property
    def value(self) -> Optional:
        return self._value

    @property
    def model(self) -> type:
        return self._model

    def set_related_name(
            self,
            related_name: str,
    ):
        self._related_name = related_name

    @property
    def related_name(self) -> str:
        return self._related_name

    @property
    def ondelete(self) -> str | None:
        return self._ondelete

    @property
    def sql_value(self) -> Optional:
        if self._value is None:
            return None

        return self._value.primary_key.sql_value

    def __eq__(self, other):
        return isinstance(other, ForeignKey) and \
            other.model == self._model and \
            other.related_name == self.related_name

    def __str__(self):
        return 'INTEGER'
