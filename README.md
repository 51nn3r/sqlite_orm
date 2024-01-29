# Define table:
```
from sqlite_orm.model import Model
from sqlite_orm.columns.string_field import StringField

from sqlite_orm.engine import engine


class Cat(Model):
    def __set_columns__(self):
        self.name = StringField()


engine.register_all(Cat)
```

# Create table:

When you will start work with model, table will be created automatically.


# Save model
`Cats(name='Tom').save()`

# Select:

```
cat = Cats(name='Tom').one()
cats = Cats().all()
```

When you call Model.all() you get a simple python list type as result. It doesn't have Model's methods.


# Update:
```
cat = Cats(name='Tom').one()
cat.update(name='Leo')
```
OR
```
cat = Cats(name='Tom').one()
cat.name = 'Leo'
cat.update()
```
OR

Set name 'Leo' for all cats with name 'Tom'
```
cats = Cats(name='Tom').update(name='Clone')
```
OR
```
cats = Cats(name='Tom')
for cat in cats:
    cat.update(name='Leo')
```

# Delete

delete all
```
Cats().delete()
```
delete all Toms
```
Cats(name='Tom').delete()
```
delete one Tom
```
Cats(name='Tom').one().delete()
```
or better
```
Cats(id=1337).delete()
```
also available
```
Cats(id=1337).one().delete()
```

# Database name
Default name is db.sqlite3, call `set_db_name()` from engine.py to change it.

```
from engine import set_db_name
set_db_name('new_db.sqlite3')
```
