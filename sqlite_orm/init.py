from sqlite_orm.engine import Engine
from sqlite_orm.engine import engine

from sqlite_orm.migrations.migration_manager import MigrationManager

from sqlite_orm.settings import DEBUG


class Init:
    _engine: Engine
    _migration_manager: MigrationManager

    def __init__(self):
        self._engine = engine
        self._migration_manager = MigrationManager()

    def register_all(self, *args):
        self._engine.register_all(*args)

        queries = self._migration_manager.check_all()
        for query in queries:
            if DEBUG:
                print(f'migration: {query}')

            self._engine.cursor.execute(query)

    @property
    def engine(self) -> Engine:
        return self._engine


init = Init()
