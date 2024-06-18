class ForeignKey:
    name: str

    def __init__(self, name):
        self.name = name

    @property
    def related_name(self):
        return self.name


class BaseModel:
    @classmethod
    def add_related_methods(cls, methods):
        for foreign_key, method in methods.items():
            bound_method = method.__get__(None, cls)
            setattr(cls, foreign_key.related_name, bound_method)

    @classmethod
    def add_dynamic_related_method(cls, foreign_key, method):
        def wrapper(self, *args, **kwargs):
            return method(self, foreign_key, *args, **kwargs)

        setattr(cls, foreign_key.related_name, wrapper)


# Пример использования
def dynamic_feedback_function(self, foreign_key):
    return f'[+] {self}: {foreign_key.related_name}'


foreign_key1 = ForeignKey("related_method1")
foreign_key2 = ForeignKey("related_method2")

BaseModel.add_dynamic_related_method(foreign_key1, dynamic_feedback_function)

new_model = BaseModel()
print(new_model.related_method1())
