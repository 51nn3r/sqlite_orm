from sqlite_orm.model import Model
from sqlite_orm.init import init
from sqlite_orm.columns.string_field import StringField
from sqlite_orm.columns.foreign_key import ForeignKey


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
        self.house = ForeignKey(House, related_name='cats', ondelete='CASCADE')


init.register_all(City, House, Cat)

city1 = City(name='sin_city').save()

house1 = House(name='pets', city=city1).save()
house2 = House(name='dead_pet', city=city1).save()

tom = Cat(name='tom', house=house2).save()
marta = Cat(name='marta', house=house1).save()

tom.update(name='tom1')
Cat(name='tom1').update(house=house1)
print(Cat().all())
print(house1.cats())
