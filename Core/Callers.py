import inspect
from enum import Enum

from Commons.Exceptions import ApplicationException
from Context.Context import ApplicationContext
from Core.Component import AbstractComponent


class Status(Enum):
    BeforeInit = 0
    Inited = 1
    Running = 2
    Stopped = 3


class ComponentWrapper:
    def __init__(self, obj: AbstractComponent):
        self.obj = obj
        self.status = Status.BeforeInit

    @property
    def context(self):
        return self.obj.context

    def setStatus(self, status: Status):
        self.status = status

    def init(self, *args, **kwargs):
        res = self.obj.init(*args, **kwargs)
        self.status = Status.Inited
        return res

    def run(self, *args, **kwargs):
        self.status = Status.Running
        res = self.obj.run(*args, **kwargs)
        self.status = Status.Stopped
        return res

    def classify(self, *args, **kwargs):
        f = None
        try:
            f = getattr(self.obj, "classify")
            if not inspect.isfunction(f) and not inspect.ismethod(f):
                raise ApplicationException(f"Caller Error: {f} is not a function, given: '{type(f)}'")
        except Exception as e:
            raise ApplicationException(f"Caller Error: there is no classfy function in {self.obj.__class__}")
        return f(*args, **kwargs)

    # TODO: multi-thread


class ComponentContainer:
    def __init__(self, context: ApplicationContext):
        self.context = context
        self.unitDict = dict()

    def updateUnitDict(self):
        for k, v in self.context.getComponentDict().items():
            if k not in self.unitDict.keys():
                unit = ComponentWrapper(v)
                unit.status = Status.BeforeInit
                self.unitDict[k] = unit

    def getComponent(self, cls):
        self.updateUnitDict()
        h = self.context.hash(cls)
        if h not in self.unitDict.keys():
            raise ApplicationException(f"Error: component with class {cls} not found")
        wrapper = self.unitDict[h]
        return wrapper

    def initComponent(self, cls):
        h = self.context.hash(cls)
        if h not in self.unitDict.keys():
            raise ApplicationException(f"Error: component with class {cls} not found")
        wrapper = self.unitDict[h]
        return wrapper.init()

    def initComponents(self):
        for k, v in self.unitDict.items():
            v.init()

    def runComponent(self, cls):
        h = self.context.hash(cls)
        if h not in self.unitDict.keys():
            raise ApplicationException(f"Error: component with class {cls} not found")
        wrapper = self.unitDict[h]
        return wrapper.run()

    def runComponents(self):
        for k, v in self.unitDict.items():
            v.init()
