import functools


class computed_property:
    # Using args in order to accept whatever attributes are given
    def __init__(self, *args):
        self.dependencies = args

    def __call__(self, function):

        # Using functools in order to preserver the docstring of the original function
        @functools.wraps(function)
        def wrapper(self):
            cache_record = []

            # For simplicity we will create a cache as an attribute of the object
            if 'cache' not in self.__dict__.keys():
                self.cache = []

            function_return = function(self)
            cache_record.append((function.__name__, function_return))
            dict_static_attributes = self.__dict__.copy().items()

            # Get values of dependency attributes
            for attribute, value in dict_static_attributes:
                # Prevent from saving the cache on itself
                if attribute != 'cache':
                    cache_record.append((attribute, value))

                    # Setter
                    if not hasattr(self, f"set_{attribute}"):
                        @functools.wraps(function)
                        def setter(value, attr=attribute):
                            setattr(self, attr, value)

                        setattr(self, f"set_{attribute}", setter)

                    # Deleter
                    if not hasattr(self, f"delete_{attribute}"):
                        @functools.wraps(function)
                        def deleter(attr=attribute):
                            delattr(self, attr)

                        setattr(self, f"delete_{attribute}", deleter)

            self.cache.append(cache_record)

            # Return the cached value
            return function_return

        return wrapper


if __name__ == "__main__":
    class Figura:
        def __init__(self, a, b):
            self.a = a
            self.b = b
        # Demonstrating that the decorator can handle attributes that do not belong to the object
        @computed_property("a", "b", "c")
        def area_quadrado(self):
            return self.a * self.b

    # Testing the wrapper
    object = Figura(5, 4)
    print(object.area_quadrado())  # Output: 25

    # Testing the setter
    object.set_a(3)

    # Testing the deleter
    object.delete_a()


