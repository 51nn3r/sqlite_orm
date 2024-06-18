from typing import List

from sqlite_orm.model import Model

from sqlite_orm.migrations.table_info import TableInfo

from sqlite_orm.engine import Engine
from sqlite_orm.engine import engine


class MigrationBuilder:
    _engine: Engine
    queries: List[str]

    def __init__(self):
        self._engine = engine
        self._queries: List[str] = []

    def check_model(
            self,
            model: Model,
    ) -> List[str]:
        model_info = TableInfo.parse_model(model)
        table_info = self.load_table_info(model.table_name)
        queries: List[str] = []

        if table_info is None:
            raise "no such table"

        for table_column in table_info.columns:
            model_column = model_info.find_column(table_column.name)
            if model_column is None:
                query = f'ALTER TABLE {model.table_name} DROP COLUMN {table_column.name};'
                queries.append(query)
                continue

            if model_column.type != table_column.type:
                raise "different column type"

            if model_column.notnull != table_column.notnull:
                raise "different not null param"

            if model_column.dflt_value != table_column.dflt_value:
                raise "different default values"

            if model_column.pk != table_column.pk:
                raise "different pk"

        for model_column in model_info.columns:
            table_column = table_info.find_column(model_column.name)
            if not table_column:
                query = f'ALTER TABLE {model.table_name} ADD COLUMN {model_column.name} {model_column.type}'
                queries.append(query)

        return queries

    def load_table_info(
            self,
            table_name: str,
    ) -> TableInfo | None:
        cursor = engine._cursor
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        if not columns:
            return None

        return TableInfo.parse_table_info(columns)
