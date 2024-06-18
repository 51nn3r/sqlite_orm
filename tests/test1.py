from sqlite_orm.model import Model
from sqlite_orm.columns.string_field import StringField
from sqlite_orm.columns.foreign_key import ForeignKey

from sqlite_orm.init import init


class House(Model):
    def __set_columns__(self):
        self.name = StringField()


class Cat(Model):
    def __set_columns__(self):
        self.name = StringField()
        self.house = ForeignKey(House, ondelete='CASCADE')


engine = init.engine
engine.register_all(House, Cat)
print('========================')

print(engine._models)

''''''
house1 = House(name='pets').save()
house2 = House(name='dead_pet').save()
print(Cat(name='Tom', house=house2))
tom = Cat(name='Tom', house=house1).save()
marta = Cat(name='Marta', house=house2).save()

print('==========================')
print(marta)
print(marta.columns[-1].value)
print(house1.cat_set())
print(house2.cat_set())
print(House(name='pets').one().cat_set())
