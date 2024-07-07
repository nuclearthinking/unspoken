from abc import ABCMeta


class SingletonMeta(type):
    """
    This is a metaclass that ensures only one instance of a class is created.
    Usage:
        class MyClass(metaclass=SingletonMeta):
            pass
    """

    _instances = {}

    def __new__(cls, name, bases, dct):
        instance = super().__new__(cls, name, bases, dct)
        return instance

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonABCMeta(SingletonMeta, ABCMeta):
    """
    This is useful for creating singleton classes that inherit from ABC.
    Usage:
        class MyClass(metaclass=SingletonABCMeta):
            pass
    """

    def __new__(cls, name, bases, dct):
        return super(SingletonABCMeta, cls).__new__(cls, name, bases, dct)

    def __init__(cls, name, bases, dct):
        super(SingletonABCMeta, cls).__init__(name, bases, dct)
