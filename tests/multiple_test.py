import unittest

from sqlite_orm.model import Model
from sqlite_orm.engine import engine
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


class MultipleTest(unittest.TestCase):
    def test1(self):
        engine.register_all(City, House, Cat)

        city1 = City(name='sign_city').save()

        house1 = House(name='pets', city=city1).save()
        house2 = House(name='dead_pet', city=city1).save()

        tom = Cat(name='tom', house=house2).save()
        marta = Cat(name='marta', house=house1).save()

        tom.update(name='tom1')
        self.assertEqual(tom.name, 'tom1')
        self.assertEqual(Cat(id=1).one().name, 'tom1')
        self.assertEqual(Cat(id=1).all()[0].name, 'tom1')

        Cat(name='tom1').one().update(name='tom2')
        self.assertEqual(Cat(id=1).one().name, 'tom2')
        self.assertEqual(Cat(id=1).all()[0].name, 'tom2')

        Cat(name='tom2').update(house=house1)
        self.assertEqual(len(house1.cats()), 2)
        self.assertEqual(len(House(name='pets').cats()), 2)

        Cat(name='tom2').update(house=house2)

        for house in City(name='sign_city').houses():
            self.assertEqual(len(house.cats()), 1)

        self.assertEqual(len(House().all()), 2)
        self.assertEqual(len(Cat().all()), 2)
        City(name='sign_city').delete()
        self.assertEqual(len(House().all()), 0)
        self.assertEqual(len(Cat().all()), 0)
