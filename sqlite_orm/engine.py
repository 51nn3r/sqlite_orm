from typing import List

import sqlite3

from sqlite_orm.columns.column import Column
from sqlite_orm.columns.foreign_key import ForeignKey

from sqlite_orm.settings import DATABASE_FILE
from sqlite_orm.settings import CONNECTION_WAITING_TIMEOUT
from sqlite_orm.settings import SQLITE_TYPES
from sqlite_orm.settings import DEBUG


def compute_query_args(active_columns: List[Column]):
    query_args = []
    for column in active_columns:
        if type(column.sql_value) in SQLITE_TYPES:
            query_args.append(column.sql_value)
        else:
            query_args.append(column.sql_value.primary_key.value)

    return query_args


class Engine:
    _connection: sqlite3.Connection
    _cursor: sqlite3.Cursor
    _models: List[type]

    def __init__(self):
        self._connection: sqlite3.Connection = sqlite3.connect(DATABASE_FILE, timeout=CONNECTION_WAITING_TIMEOUT)
        self._cursor: sqlite3.Cursor = self._connection.cursor()
        self._models: List[type] = []

        keys_on = 'PRAGMA foreign_keys = ON'
        self._cursor.execute(keys_on)

    def register_all(
            self,
            *args,
    ):
        for model in args:
            self.register_model(model)

        for model in args:
            self.create(model())

    def register_model(
            self,
            model_type: type,
    ):
        model = model_type()
        if model_type is None or model_type in self._models:
            return

        self._models.append(model_type)

        # parse foreign keys
        for column in model.columns:
            if isinstance(column, ForeignKey):
                if column.related_name is None:
                    column.set_related_name(f'{model.table_name}_set')

                column.model.add_related_method(column)

    def __del__(self):
        self._cursor.close()
        self._connection.close()

    def create(self, model):
        query = f'CREATE TABLE IF NOT EXISTS {model.table_name} ('
        for column in model.columns:
            query += f'{column.name} {column} '
            for attr in column.attributes:
                query += f'{attr} '

            query = f'{query[:-1]}, '

        for column in model.columns:
            if isinstance(column, ForeignKey):
                query += f'FOREIGN KEY ({column.name}) REFERENCES {column.model().table_name} ' \
                         f'({column.model().primary_key.name})'

                if column.ondelete is not None:
                    query += f' ON DELETE {column.ondelete}, '
                else:
                    query += ', '

        query = f'{query[:-2]});'
        if DEBUG:
            print(query)

        self._cursor.execute(query)

    def one(
            self,
            model,
    ):
        active_columns = [column for column in model.columns if column.value is not None]
        query = f'SELECT * FROM {model.table_name}'

        if active_columns:
            query += ' WHERE ' + f'{" AND ".join([f"{column.name}=?" for column in active_columns])};'
        else:
            query += ';'

        query_args = compute_query_args(active_columns)
        if DEBUG:
            print(query, query_args)

        self._cursor.execute(query, query_args)
        _one = self._cursor.fetchone()

        return _one

    def all(
            self,
            model,
    ):
        active_columns = [column for column in model.columns if column.value is not None]
        query = f'SELECT * FROM {model.table_name}'

        if active_columns:
            query += ' WHERE ' + f'{" AND ".join([f"{column.name}=?" for column in active_columns])};'
        else:
            query += ';'

        query_args = compute_query_args(active_columns)
        if DEBUG:
            print(query, query_args)

        self._cursor.execute(query, query_args)
        _all = self._cursor.fetchall()

        return _all

    def save(
            self,
            model,
    ):
        active_columns = [column for column in model.columns if column.value is not None]
        query = f'INSERT INTO {model.table_name} (' \
                f'{", ".join([column.name for column in active_columns])}) ' \
                f'VALUES ({", ".join(["?" for _ in active_columns])});'

        query_args = compute_query_args(active_columns)
        if DEBUG:
            print(query, query_args)

        self._cursor.execute(query, query_args)
        self._connection.commit()

        last_row_id = self._cursor.lastrowid
        model.set_primary_key(last_row_id)
        setattr(model, model.primary_key.name, last_row_id)

    def delete(
            self,
            model,
    ):
        active_columns = [column for column in model.columns if column.value is not None]
        query = f'DELETE FROM {model.table_name}'

        if active_columns:
            query += f' WHERE {"=? AND ".join([column.name for column in active_columns])}=?;'
        else:
            query += ';'

        query_args = compute_query_args(active_columns)
        if DEBUG:
            print(query, query_args)

        self._cursor.execute(query, query_args)
        self._connection.commit()

    def update(
            self,
            model,
            **kwargs,
    ):
        active_columns = [column for column in model.columns if column.value is not None]
        active_columns_vals = [column.sql_value for column in active_columns]

        # parse kwargs
        for column in model.columns:
            if column.name in kwargs:
                column.set_value(kwargs[column.name])

        changed_columns = [column for column in model.columns if column.name != model.primary_key.name
                           and column.value is not None]

        if model.primary_key.sql_value is None:
            query = f'UPDATE {model.table_name} SET {"=?, ".join([column.name for column in changed_columns])}=? ' \
                    f'WHERE {"=? AND ".join([column.name for column in active_columns])}=?;'

            if DEBUG:
                print(query, [column.sql_value for column in changed_columns] + active_columns_vals)

            self._cursor.execute(query, [column.sql_value for column in changed_columns] + active_columns_vals)
            self._connection.commit()
        else:
            query = f'UPDATE {model.table_name} SET {"=?, ".join([column.name for column in changed_columns])}=? ' \
                    f'WHERE {model.primary_key.name}=?;'

            if DEBUG:
                print(query, [column.sql_value for column in changed_columns] + [model.primary_key.sql_value])

            self._cursor.execute(query, [column.sql_value for column in changed_columns] +
                                 [model.primary_key.sql_value])
            self._connection.commit()

    @property
    def models(self):
        return self._models

    @property
    def cursor(self):
        return self._cursor


engine: Engine = Engine()
