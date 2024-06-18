from __future__ import annotations

from typing import List
from typing import Callable

from sqlite_orm.engine import Engine
from sqlite_orm.engine import engine
from sqlite_orm.columns.column import Column
from sqlite_orm.columns.integer_field import IntegerField
from sqlite_orm.columns.foreign_key import ForeignKey
from sqlite_orm.column_attributes.primary_key import PRIMARY_KEY
from sqlite_orm.column_attributes.autoincrement import AUTOINCREMENT
from sqlite_orm.column_attributes.not_null import NOT_NULL

from sqlite_orm.settings import PRIMARY_KEY_DEFAULT_NAME
from sqlite_orm.settings import DEBUG

class Model:
    _columns: List[Column]
    _primary_key: Column | None
    _table_name: str
    _engine: Engine

    def __set_columns__(self):
        '''
        Use this function to set columns to your table. You can also set them without any function
        but this way the order of columns may be random

        Example:

        class Cats(Model):
            def __set_columns__(self):
                self.id = Column(Integer, primary_key=True)
                self.name = Column(String)

        :return:
        '''

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        COLUMN_NAMES_BLACKLIST = dir(self)
        self._engine = engine
        self._columns: List[Column] = []
        self._primary_key = None
        self._table_name = self.compute_table_name()
        self.__set_columns__()
        # self._engine.set_feedbacks(self)
        _args = list(args)

        columns = []
        for (column_name, column) in self.__dict__.items():
            if not isinstance(column, Column):
                continue

            if column_name in COLUMN_NAMES_BLACKLIST:
                raise "bad column name"

            if PRIMARY_KEY in column.attributes:
                if self._primary_key is not None:
                    raise "multiple primary keys"

                self._primary_key = column

            if isinstance(column, ForeignKey):
                column.set_bound_model(self.__class__)

            column.set_name(name=column_name)
            columns.append(column)

        if self._primary_key is None:
            pk_column_name = self._generate_unique_column_name(PRIMARY_KEY_DEFAULT_NAME)
            pk_column = IntegerField(PRIMARY_KEY, AUTOINCREMENT, NOT_NULL)
            pk_column.set_name(pk_column_name)
            if pk_column_name in kwargs:
                pk_column.set_value(kwargs[pk_column_name])
                setattr(self, pk_column_name, pk_column.value)
            else:
                setattr(self, pk_column_name, None)
            self._columns.append(pk_column)
            self._primary_key = pk_column

        for column in columns:
            if args:
                column.set_value(_args.pop(0))

            if column.name in kwargs:
                column.set_value(kwargs[column.name])

                if isinstance(column, ForeignKey):
                    dst_model = column.model
                    kwargs = {dst_model().primary_key.name: column.value}
                    column.set_value(dst_model(**kwargs).one())

            setattr(self, column.name, column.value)

            self._columns.append(column)

    @staticmethod
    def update_columns(func):
        def wrapper(self: Model, **kwargs):
            for column in self.columns:
                if column.name in kwargs:
                    new_value = kwargs[column.name]
                    column.set_value(new_value)
                    setattr(self, column.name, new_value)
                elif hasattr(self, column.name):
                    column.set_value(getattr(self, column.name))
            return func(self)

        return wrapper

    def set_primary_key(
            self,
            value,
    ):
        self._primary_key.set_value(value)

    @property
    def table_name(self) -> str:
        return self._table_name

    @property
    def columns(self) -> List[Column]:
        return self._columns

    @property
    def primary_key(self):
        return self._primary_key

    @update_columns
    def one(self) -> Model | None:
        _one = self._engine.one(self)
        if _one is None:
            return None

        column_names = [column.name for column in self.columns]
        kwargs = {name: column_val for name, column_val in zip(column_names, _one)}
        return self.__class__(**kwargs)

    @update_columns
    def all(self) -> List[Model]:
        _all = self._engine.all(self)

        models: List[Model] = []
        for _one in _all:
            column_names = [column.name for column in self.columns]
            kwargs = {name: column_val for name, column_val in zip(column_names, _one)}
            models.append(self.__class__(**kwargs))

        return models

    @update_columns
    def save(self):
        self._engine.save(self)
        return self

    @update_columns
    def delete(self):
        self._engine.delete(self)

    def update(self, **kwargs) -> Model:
        for column in self._columns:
            if column.name in kwargs:
                setattr(self, column.name, kwargs[column.name])

        self._engine.update(self, **kwargs)
        return self

    @property
    def _feedback(self):
        return None

    def _generate_unique_column_name(self, base=''):
        column_names = [column.name for column in self._columns]
        postfix = 0
        name = base
        while name in column_names:
            name = f'{base}_{postfix}'
            postfix += 1

        return name

    @classmethod
    def compute_table_name(cls):
        return cls.__name__.lower()

    @classmethod
    def add_related_method(
            cls,
            foreign_key: ForeignKey,
    ):
        def related_method(
                self,
        ):
            related_model = foreign_key.bound_model
            kwargs = {foreign_key.name: self.primary_key.value}
            if DEBUG:
                print(kwargs)

            return related_model(**kwargs).all()

        setattr(cls, foreign_key.related_name, related_method)

    def __str__(self):
        return '{' + f'{self._table_name}: ' + ', '.join([f'{column.name}={getattr(self, column.name)}'
                                                          for column in self._columns]) + '}'

    def __repr__(self):
        return '{' + f'{self._table_name}: ' + ', '.join([f'{column.name}={getattr(self, column.name)}'
                                                          for column in self._columns]) + '}'
