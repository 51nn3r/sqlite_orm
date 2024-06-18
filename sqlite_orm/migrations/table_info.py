from __future__ import annotations

from typing import List

from sqlite_orm.model import Model
from sqlite_orm.migrations.column_info import ColumnInfo


class TableInfo:
    _columns: List[ColumnInfo]

    def __init__(self):
        self._columns: List[ColumnInfo] = []

    @classmethod
    def parse_model(
            cls,
            model: Model,
    ) -> TableInfo:
        table_info = TableInfo()
        table_info._parse_model(model)
        return table_info

    @classmethod
    def parse_table_info(
            cls,
            table_info_arg: List[List[int | str | None]],
    ) -> TableInfo:
        table_info = TableInfo()
        table_info._parse_table_info(table_info_arg)
        return table_info

    def _parse_model(
            self,
            model: Model
    ):
        self._columns.clear()
        for cid, column in enumerate(model.columns):
            self._columns.append(ColumnInfo.load_column(cid, column))

    def _parse_table_info(
            self,
            table_info: List[List[int | str | None]],
    ):
        self._columns.clear()
        for column_info in table_info:
            self._columns.append(ColumnInfo.load_table_info(column_info))

    def find_column(
            self,
            name: str,
    ):
        for column in self._columns:
            if column.name == name:
                return column

        return None

    @property
    def columns(self) -> List[ColumnInfo]:
        return self._columns
