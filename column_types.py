from datetime import datetime


class Type:
    def to_db(self, value):
        return value

    def to_python(self, value):
        return value


class Integer(Type):
    def __str__(self):
        return 'INTEGER'


class String(Type):
    def __str__(self):
        return 'TEXT'


class Bool(Type):
    def __str__(self):
        return 'INTEGER'

    def to_db(self, value):
        return bool(value)

    def to_python(self, value):
        return int(value)


class DateTime(Type):
    def __str__(self):
        return 'TEXT'

    def to_db(self, value):
        return datetime.strftime(value, '%Y-%m-%d %H:%M:%S.%f')

    def to_python(self, value):
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
