import re
from datetime import datetime

from sqlite_orm.columns.column import Column


class DatetimeField(Column):
    _value: datetime | None

    def __init__(
            self,
            *args,
            **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._value: int | None = None

    def set_value(
            self,
            value: str | datetime,
    ):
        if isinstance(value, datetime):
            self._value = value
            return

        datetime_formate1 = r'\d{4}-\d{1,2}-\d{1,2}\ \d{1,2}\:\d{1,2}\:\d{1,2}$'
        datetime_formate2 = r'\d{4}-\d{1,2}-\d{1,2}\ \d{1,2}\:\d{1,2}\:\d{1,2}\.\d{6}$'

        if re.search(datetime_formate1, value):
            self._value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        elif re.search(datetime_formate2, value):
            self._value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        else:
            raise "invalid date formate"

    @property
    def value(self):
        return self._value

    @property
    def sql_value(self):
        return datetime.strftime(self._value, '%Y-%m-%d %H:%M:%S.%f')

    def __str__(self):
        return 'TEXT'
