from abc import  ABCMeta,abstractmethod
class Singleton(metaclass=ABCMeta):
    _instances = None
    @classmethod
    def getInstance(cls,*args,**kwargs):
        if cls._instances is None:
            cls._instances = cls(*args,**kwargs)
        return cls._instances


