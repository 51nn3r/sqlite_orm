from typing import List
from typing import Optional

from sqlite_orm.column_attributes.default import DEFAULT
from sqlite_orm.column_attributes.primary_key import PRIMARY_KEY
from sqlite_orm.column_attributes.required import REQUIRED
from sqlite_orm.column_attributes.column_attribute import ColumnAttribute


class Column:
    _name: str | None
    _attributes: List[ColumnAttribute]

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        self._name = None
        self._attributes = [a for a in args if isinstance(a, ColumnAttribute)]

        supported_kwargs = [
            'default',
            'primary_key',
            'required',
        ]
        column_kwargs = {
            k: kwargs[k] for k in kwargs if k in supported_kwargs
        }
        other_kwargs = {
            k: kwargs[k] for k in kwargs if k not in supported_kwargs
        }

        for attribute_name, attribute in column_kwargs.items():
            if not isinstance(attribute, ColumnAttribute):
                if attribute_name == 'default':
                    self._attributes.append(DEFAULT)
                if attribute_name == 'primary_key':
                    self._attributes.append(PRIMARY_KEY)
                if attribute_name == 'required':
                    self._attributes.append(REQUIRED)
            else:
                self._attributes.append(attribute)

    def set_name(
            self,
            name: str,
    ):
        if self._name is not None:
            raise "column name has already been defined"

        self._name = name

    @property
    def name(self) -> str | None:
        return self._name

    @property
    def attributes(self) -> List[ColumnAttribute]:
        return self._attributes

    def set_value(self, value):
        pass

    @property
    def value(self) -> Optional:
        return None

    @property
    def sql_value(self) -> Optional:
        return None

    def __str__(self):
        if self._name is None:
            return 'None'

        return self._name

    def __repr__(self):
        if self._name is None:
            return 'None'

        return self._name
