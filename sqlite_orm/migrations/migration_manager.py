from typing import List

from sqlite_orm.migrations.migration_builder import MigrationBuilder


class MigrationManager(MigrationBuilder):
    def check_all(self) -> List[str]:
        migrations = []
        for model_cls in self._engine.models:
            queries = self.check_model(model_cls())
            migrations += queries

        return migrations
