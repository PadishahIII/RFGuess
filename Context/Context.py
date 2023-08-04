import typing

from Commons.Exceptions import ContextException



# Context store and read instances. cannot write
class Context:
    def __init__(self):
        self.instances = {}

    def getInstance(self, cls, *args, **kwargs):
        h = self.hash(cls)
        if h not in self.instances:
            self.instances[h] = cls(*args, **kwargs)
        return self.instances[h]

    def getExistingInstance(self, cls):
        h = self.hash(cls)
        if h not in self.instances:
            return None
        return self.instances[h]

    # update or create instance
    def storeInstance(self, cls, obj):
        self.instances[self.hash(cls)] = obj

    def hash(self, cls):
        return id(cls)


class ApplicationContext(Context, Exception):
    ABSTRACTCOMPONENT = False

    def __init__(self):
        super().__init__()
        self.componentDict = dict()

    # Get Existing Component

    def getComponent(self, cls) :
        if cls is None:
            raise ContextException(f"component class cannot be None")
        if cls not in self.componentDict.keys():
            raise ContextException(f"not found component with class {type(cls)}")
        obj = self.getExistingInstance(cls)
        if obj is None:
            raise ContextException(f"not found component with class {type(cls)}")
        if ApplicationContext.ABSTRACTCOMPONENT is False:
            from Core.Component import AbstractComponent
            ABSTRACTCOMPONENT = True
        if not isinstance(obj, AbstractComponent):
            raise ContextException(
                f"Error Invaild component class: expected: {AbstractComponent}, given: {type(obj)}"
            )
        return obj

    def getComponentDict(self) -> typing.Dict[str, typing.Any]:
        if ApplicationContext.ABSTRACTCOMPONENT is False:
            from Core.Component import AbstractComponent
            ABSTRACTCOMPONENT = True
        for k, v in self.instances.items():
            if isinstance(v, AbstractComponent):
                self.componentDict[k] = v

        return self.componentDict

    # Get Bean, must exist
    def getBean(self, cls):
        if cls == None:
            raise ContextException(f"bean class cannot be None")
        h = self.hash(cls)
        if h not in self.instances.keys():
            raise ContextException(f"not found bean with class {type(cls)}")
        obj = self.getExistingInstance(cls)
        if obj is None:
            raise ContextException(f"Error: cannot get bean with class {type(cls)}")
        return obj


class BasicContext:
    def __init__(self):
        self._ctx: ApplicationContext = None

    @property
    def context(self):
        return self._ctx

    @context.setter
    def context(self, ctx: ApplicationContext):
        self._ctx = ctx
