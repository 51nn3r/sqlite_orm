from sqlite_orm.model import Model
from sqlite_orm.columns.string_field import StringField
from sqlite_orm.columns.foreign_key import ForeignKey

from sqlite_orm.init import init


class City(Model):
    def __set_columns__(self):
        self.name = StringField()


class House(Model):
    def __set_columns__(self):
        self.name = StringField()
        self.city = ForeignKey(City, related_name='houses', ondelete='CASCADE')


class Cat(Model):
    def __set_columns__(self):
        self.name = StringField()
        # self.test = StringField()
        self.house = ForeignKey(House, related_name='cats', ondelete='CASCADE')


init.register_all(City, House, Cat)
