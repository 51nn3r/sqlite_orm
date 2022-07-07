from column_attributes import *
import sqlite3

DATABASE_FILE = ':memory:'
DATABASE_FILE = 'db.sqlite3'
CONNECTION_WAITING_TIMEOUT = 600


def set_db_name(new_name):
    global DATABASE_FILE
    DATABASE_FILE = new_name


class Engine:
    connection = None
    cursor = None
    FIELDS_NAMES_BLACKLIST = []

    def __init__(self):
        self.FIELDS_NAMES_BLACKLIST = dir(self)

    def open_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect(DATABASE_FILE, timeout=CONNECTION_WAITING_TIMEOUT)
            self.cursor = self.connection.cursor()

    def close_connection(self):
        if self.connection is not None:
            self.cursor.close()
            self.connection.close()
            self.cursor = None
            self.connection = None


class Column:
    name = None
    value = None
    db_value = None
    is_empty = True

    def __init__(self, type=None, **kwargs):
        self.type = type()
        # Parse column attributes
        self.attrs = []
        self.all_attrs = {}
        if 'primary_key' in kwargs:
            primary_key = PrimaryKey()
            self.__setattr__('primary_key', primary_key)
            self.attrs.append(primary_key)
            self.all_attrs.update({'primary_key': True})
        if 'default' in kwargs:
            default = Default(default=kwargs['default'])
            self.__setattr__('default', default)
            self.attrs.append(default)
            self.all_attrs.update({'default': default.default_value})
        if 'required' in kwargs:
            required = Required()
            self.__setattr__('required', required)
            self.attrs.append(required)
            self.all_attrs.update({'required': True})
        if 'foreign_key' in kwargs:
            self.foreign_key = ForeignKey(**kwargs)
            self.all_attrs.update({'foreign_key': self.foreign_key.key_destination})
            if self.foreign_key.ondelete:
                self.all_attrs.update({'ondelete': self.foreign_key.ondelete})

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return int(self.value)

    '''
    def __repr__(self):
        return self.name
    '''


class Model(Engine):
    __tablename__ = None

    def __set_columns__(self):
        '''
        Use this function to set columns to your table. You can also set them without any function
        but this way the order of columns may be random

        Example:

        class Cats(Model):
            __tablename__ = 'cats'

            def __set_columns__(self):
                self.id = Column(Integer, primary_key=True)
                self.name = Column(String)

        :return:
        '''

    def __init__(self, **kwargs):
        super(Model, self).__init__()

        for key in kwargs:
            assert key not in self.FIELDS_NAMES_BLACKLIST, f'Bad field name: {key}'

        if '__tablename__' in kwargs:
            self.__tablename__ = kwargs['__tablename__']
        # Define columns
        self.columns = []
        # If __set_columns__ is redefined try to use it
        self.__set_columns__()
        for (attr_name, attr) in self.__dict__.items():
            if type(attr) == Column:
                attr = Column(type(attr.type), **attr.all_attrs)
                attr.name = attr_name
                if attr_name in kwargs:
                    attr.value = kwargs[attr_name]
                    attr.db_value = attr.type.to_db(kwargs[attr_name])
                    attr.is_empty = False
                if hasattr(attr, 'foreign_key'):
                    attr.foreign_key.column_name = attr_name
                self.columns.append(attr)
                self.__setattr__(attr_name, attr.value)
        # If __set_columns is not redefined search for any columns
        if not self.columns:
            start_attrs = dir(self)
            for attr_name in start_attrs:
                attr = getattr(self, attr_name)
                if type(attr) == Column:
                    '''
                    I don't exactly know how it works but without next line program somehow reuse memory
                    and when I try create another Model child obj for ex in all() it create ony href to original 
                    and then change original. Maybe after some time I'll understand how this shit works
                    but now I have to use this crutch. Sorry man...
                    '''
                    attr = Column(type(attr.type), **attr.all_attrs)
                    attr.name = attr_name
                    if attr_name in kwargs:
                        attr.value = kwargs[attr_name]
                        attr.db_value = attr.type.to_db(kwargs[attr_name])
                        attr.is_empty = False
                    if hasattr(attr, 'foreign_key'):
                        attr.foreign_key.column_name = attr_name
                    self.columns.append(attr)
                    '''
                    Have to save changes in this object for comfortable using
                    because because of crutch I made, it doesn't save changes 
                    '''
                    self.__setattr__(attr_name, attr.value)
        # Get primary key column
        self.primary_key_column = None
        for column in self.columns:
            if PrimaryKey in [type(attr) for attr in column.attrs]:
                self.primary_key_column = column
                break
        assert self.primary_key_column, 'You mast set primary key column'
        self.create()

    def update_columns(func):
        def wrapper(self, **kwargs):
            for column in self.columns:
                if column.name in kwargs:
                    column.value = kwargs[column.name]
                    column.is_empty = False
                elif hasattr(self, column.name):
                    column.value = self.__getattribute__(column.name)
                    column.is_empty = False
            return func(self, **kwargs)

        return wrapper

    def create(self):
        query = f'CREATE TABLE IF NOT EXISTS {self.__tablename__} ('
        # Set columns with attributes
        for column in self.columns:
            query += f'{column.name} {column.type} '
            for attr in column.attrs:
                query += f'{attr} '
            query = f'{query[:-1]}, '
        # Set foreign keys
        for column in self.columns:
            if hasattr(column, 'foreign_key'):
                query += f'{column.foreign_key}, '
        query = query[:-2] + ');'
        self.open_connection()
        self.cursor.execute(query)
        self.close_connection()

    @update_columns
    def one(self):
        active_columns = [column for column in self.columns if not column.is_empty and column.value is not None]
        self.open_connection()
        if active_columns:
            query = f'SELECT * FROM {self.__tablename__} WHERE ' \
                    f'{" AND ".join([f"{column.name}=?" for column in active_columns])}'
            self.cursor.execute(query, [column.value for column in active_columns])
        else:
            query = f'SELECT * FROM {self.__tablename__}'
            self.cursor.execute(query)
        args = self.cursor.fetchone()
        self.close_connection()
        if args:
            kwargs = {}
            for index in range(0, len(self.columns)):
                if args[index] is not None:
                    kwargs.update({self.columns[index].name: self.columns[index].type.to_python(args[index])})
            return self.__class__(**kwargs)
        return None

    @update_columns
    def all(self, order_by=None, order_as=None):
        active_columns = [column for column in self.columns if not column.is_empty and column.value is not None]
        self.open_connection()
        if active_columns:
            query = f'SELECT * FROM {self.__tablename__} WHERE ' \
                    f'{" AND ".join([f"{column.name}=?" for column in active_columns])}'
        else:
            query = f'SELECT * FROM {self.__tablename__}'
        if order_by:
            if type(order_by) == list:
                query += f' ORDER BY {", ".join(column_name for column_name in order_by)}'
            else:
                query += f' ORDER BY {order_by}'
            if order_as == 'asc':
                query += ' ASC'
            elif order_as == 'desc':
                query += ' DESC'
        query += ';'
        self.cursor.execute(query, [column.value for column in active_columns])
        args_set = self.cursor.fetchall()
        self.close_connection()
        kwargs_set = []
        for args in args_set:
            kwargs = {}
            for index in range(0, len(self.columns)):
                if args[index] is not None:
                    kwargs.update({self.columns[index].name: self.columns[index].type.to_python(args[index])})
            kwargs_set.append(kwargs)
        return [self.__class__(**kwargs) for kwargs in kwargs_set]

    @update_columns
    def save(self):
        active_columns = [column for column in self.columns if
                          not column.is_empty and column.value is not None and column is not self.primary_key_column]
        # assert active_columns, 'No insert info, write anything'
        query = f'INSERT INTO {self.__tablename__} (' \
                f'{", ".join([column.name for column in active_columns])}) ' \
                f'VALUES ({", ".join(["?" for column in active_columns])});'
        self.open_connection()
        self.cursor.execute(query, [column.db_value for column in active_columns])
        self.connection.commit()
        self.__setattr__(self.primary_key_column.name, self.cursor.lastrowid)
        self.close_connection()
        for index in range(0, len(self.columns)):
            if self.columns[index].name == self.primary_key_column.name:
                self.columns[index].value = self.__getattribute__(self.primary_key_column.name)
        return self

    @update_columns
    def update(self, **kwargs):
        for key in kwargs:
            assert key not in self.FIELDS_NAMES_BLACKLIST, f'Bad field name: {key}'
        for column in self.columns:
            if column.name in kwargs:
                self.__setattr__(column.name, column.value)
                column.value = kwargs[column.name]
                column.is_empty = False
            elif hasattr(self, column.name):
                column.value = self.__getattribute__(column.name)
                column.is_empty = False
        active_columns = [column for column in self.columns if
                          not column.is_empty and column.value is not None and column is not self.primary_key_column]
        query = f'UPDATE {self.__tablename__} SET {"=?, ".join([column.name for column in active_columns])}=? ' \
                f'WHERE {self.primary_key_column.name}=?;'
        query_args = [column.value for column in active_columns]
        query_args.append(self.primary_key_column.value)
        self.open_connection()
        self.cursor.execute(query, query_args)
        self.connection.commit()
        self.close_connection()
        return self

    @update_columns
    def delete(self):
        active_columns = [column for column in self.columns if not column.is_empty and column.value is not None]
        if active_columns:
            query = f'DELETE FROM {self.__tablename__} WHERE ' \
                    f'{"=? AND ".join([column.name for column in active_columns])}=?;'
        else:
            query = f'DELETE FROM {self.__tablename__}'
        self.open_connection()
        self.cursor.execute(query, [column.value for column in active_columns])
        self.connection.commit()
        self.close_connection()
