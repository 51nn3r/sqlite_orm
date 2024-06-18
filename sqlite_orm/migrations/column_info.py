from __future__ import annotations
from typing import List

from sqlite_orm.columns.column import Column

from sqlite_orm.column_attributes.not_null import NotNull
from sqlite_orm.column_attributes.default import Default
from sqlite_orm.column_attributes.primary_key import PrimaryKey


class ColumnInfo:
    cid: int
    name: str
    type: str
    notnull: NotNull | None
    dflt_value: Default | None
    pk: PrimaryKey | None

    @classmethod
    def load_column(
            cls,
            cid: int,
            column: Column,

    ):
        column_info = ColumnInfo()
        column_info._load_column(cid, column)
        return column_info

    @classmethod
    def load_table_info(
            cls,
            table_info: List[int | str | None],
    ):
        column_info = ColumnInfo()
        column_info._load_table_info(table_info)
        return column_info

    def _load_column(
            self,
            cid: int,
            column: Column,
    ):
        column_info = ColumnInfo
        self.cid = cid
        self.name = column.name
        self.type = column.type
        self.notnull = None
        self.dflt_value = None
        self.pk = None
        for attr in column.attributes:
            if isinstance(attr, NotNull):
                self.notnull = attr
            elif isinstance(attr, Default):
                self.dflt_value = attr
            elif isinstance(attr, PrimaryKey):
                self.pk = attr

    def _load_table_info(
            self,
            table_info: List[int | str | None]
    ):
        if len(table_info) != 6:
            raise "invalid table info"

        self.cid = table_info[0]
        self.name = table_info[1]
        self.type = table_info[2]
        self.notnull = NotNull() if table_info[3] else None
        dftl_value = table_info[4]
        self.dflt_value = Default(dftl_value) if dftl_value else None
        self.pk = PrimaryKey() if table_info[5] else None
