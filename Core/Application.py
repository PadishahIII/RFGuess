import inspect
import typing

import Core.Utils as Utils
from Commons.Exceptions import *
from Context.Container import Container
from Context.Context import ApplicationContext
from Core.Callers import ComponentContainer
from Core.Callers import ComponentWrapper
from Core.Component import *
from Core.Config import ApplicationConfig, DefaultApplicationConfig


class SlotUnit:
    def __init__(self, decoratorUnit: Utils.DecoratorUnit, classObj=None, paramClass=None, paramStr: str = None):
        self.decoratorUnit = decoratorUnit
        self.classObj = classObj
        self.paramClass = paramClass
        self.paramClassName = paramStr


class Application:
    def __init__(self):
        self.context = ApplicationContext()
        self.container = Container(self.context)
        self.componentContainer = ComponentContainer(self.context)
        self.configIns: ApplicationConfig = DefaultApplicationConfig()

        # self.beanObjList = list()
        self.beanClassList = list()
        self.componentClassList = list()
        self.autowireUnitList: typing.List[Utils.DecoratorUnit] = list()
        self.slotList: typing.List[SlotUnit] = list()
        self.slotDict: typing.Dict[str, SlotUnit] = dict()

    def scanAnnotation(self, annoName: str, package: str):
        pass

    def analyzeDecorators(self):
        self.beanClassList = Utils.beanClassList
        self.autowireUnitList = Utils.autowireClassNameList
        componentList = Utils.componentClassList

        # register beans
        for cls in self.beanClassList:
            if not inspect.isclass(cls):
                raise InitializationException(f"Error Bean: not a class ({cls}:{type(cls)})")
            # register bean object into container
            self.container.register(cls)
            # self.container.resolve(cls)

        # register Component to dependency
        # store default instance in Context if there is no register before
        for component in componentList:
            if not inspect.isclass(component):
                raise InitializationException(f"Error Component: not a class ({component}:{type(component)}")
            self.componentClassList.append(component)
            self.container.register(component)
            # store component obj to Context, otherwise it'll only exist in container but not in Context
            self.container.resolve(component)

        # get all slots
        for unit in self.autowireUnitList:
            if not isinstance(unit, Utils.DecoratorUnit):
                raise InitializationException(f"Error unit: not a unit ({unit}:{type(unit)}:{unit.__dict__}")
            # slots to be injected
            slot = self.getSlot(unit)
            if slot == None or not isinstance(slot, SlotUnit):
                raise InitializationException(f"Error slot: None slot or not a Slot ({slot}")
            # slot can only in Components
            cls = slot.classObj
            if cls not in self.componentClassList:
                raise InitializationException(f"Error: slot can only in Components, {cls} is not a Component")
            self.slotList.append(slot)
            # Build Slot dict
            funcFullName = self.getFullFuncName(slot)
            self.slotDict[funcFullName] = slot

    def getSlot(self, unit: Utils.DecoratorUnit) -> SlotUnit:
        packageName = unit.packageName
        moduleName = unit.moduleName
        module = __import__(packageName + "." + moduleName)
        clsObj = self.getClass(module, moduleName, unit.className)
        d = self.getParamOfFunc(unit.funcObj)
        if d == None or len(d) <= 0:
            raise InitializationException(
                f"@Autowire must decorate a setter with at least one param, given({packageName + '.' + moduleName + '.' + unit.className}):\n{inspect.getsource(unit.funcObj)}")
        paramClassName, paramClass = d.popitem()

        slot = SlotUnit(unit, classObj=clsObj, paramClass=paramClass, paramStr=paramClassName)
        return slot

    def getParamOfFunc(self, func) -> dict:
        if not (inspect.isfunction(func) or inspect.ismethod(func)):
            raise Exception(f"get function param Error: not a function, given {type(func)}:{func}")
        args = inspect.getfullargspec(func)
        d = dict()
        if args.annotations != None:
            for paramName, paramClass in args.annotations.items():
                if paramName != 'return':
                    d[paramName] = paramClass
            return d
        else:
            return None

    def getClass(self, module, moduleName: str, className: str):
        m = getattr(module, moduleName)
        cls = getattr(m, className)
        # cls = globals()[className]
        # print(cls)
        return cls

    def searchSlot(self, funcName):
        funcNameList = [slot.decoratorUnit.funcName for slot in self.slotList if
                        slot.decoratorUnit.funcName != None and len(slot.decoratorUnit.funcName) > 0]

    def getFullFuncName(self, slot: SlotUnit) -> str:
        unit = slot.decoratorUnit
        return unit.packageName + "." + unit.moduleName + "." + unit.funcName + ":" + slot.paramClassName

    def loadConfig(self):
        # scan config annotation and store the instance
        # self.configIns = None
        pass

    def injectDependencyToSlots(self):
        for slot in self.slotList:
            unit = slot.decoratorUnit
            cls = slot.classObj
            funcName = unit.funcName
            funcObj = unit.funcObj
            dependencyClass = slot.paramClass
            dependencyObj = None

            if cls == None or not inspect.isclass(cls):
                raise InitializationException(f"Error slot class is None or invaild type: {cls}")

            if dependencyClass == None or not inspect.isclass(dependencyClass):
                raise InitializationException(f"Error dependency class is None or invaild type: {dependencyClass}")

            # initialize beans
            dependencyObj = self.getDependency(dependencyClass)
            if dependencyObj == None or not isinstance(dependencyObj, dependencyClass):
                raise InitializationException(
                    f"Error dependency object is None or invaild type: given object:{dependencyObj} with type{type(dependencyObj) if dependencyObj != None else None}, expected:{dependencyClass}")

            # if component have no slot, it won't be initialized here
            componentObj = self.getComponent(cls)
            if componentObj == None or not isinstance(componentObj, cls):
                raise InitializationException(
                    f"Error component object is None or invaild type: given object:{componentObj} with type{type(componentObj) if componentObj != None else None}, expected:{cls}")
            self.injectOneSlot(componentObj, funcName, dependencyObj)

    def injectContextToComponents(self):
        for componentCls in self.componentClassList:
            componentObj: AbstractComponent = self.getComponent(componentCls)
            if componentObj == None or not isinstance(componentObj, componentCls):
                raise InitializationException(
                    f"Error component object is None or invaild type: given object:{componentObj} with type{type(componentObj) if componentObj != None else None}, expected:{componentCls}")
            componentObj.context = self.context

    def getComponent(self, cls):
        return self.container.resolve(cls)

    def getDependency(self, cls):
        return self.container.resolve(cls)

    def injectOneSlot(self, component, funcName, denpendencyObj):
        funcObj = self.getFunc(component, funcName)
        d = self.getParamOfFunc(funcObj)
        if d == None or len(d) <= 0:
            raise InitializationException(
                f"@Autowire must decorate a setter with one param, given:\n{inspect.getsource(funcObj)}")
        paramClassName, paramClass = d.popitem()
        if not isinstance(denpendencyObj, paramClass):
            raise InitializationException(
                f"Error when inject dependency: param type not match. component expected: {paramClass}, given: {type(denpendencyObj)}")
        # Call setter
        funcObj(denpendencyObj)

    # reflect call a function of an object and get the return value
    def getFunc(self, obj, funcName):
        try:
            f = getattr(obj, funcName)
            if not inspect.isfunction(f) and not inspect.ismethod(f):
                raise Exception(f"get function param Error: not a function, given {type(f)}:{f}")
        except Exception as e:
            raise InitializationException(f"Error: object {obj} have no function named {funcName}")
        return f

    def init(self):
        # scan Beans
        self.analyzeDecorators()
        self.loadConfig()
        self.configIns.applicationConfig(self.context)  # add self-defined beans
        # scan components

        # inject dependencies
        self.injectDependencyToSlots()
        self.injectContextToComponents()

    def run(self):
        # run components
        pass


class ApplicationWrapper:

    def __init__(self) -> None:
        super().__init__()
        self.application = Application()

    @property
    def context(self):
        return self.application.context

    def setComponentPackages(self, packages: list):
        Utils.importModuleFromPackage(".", packages)

    # register and initialize bean
    def addBean(self, cls, *args, **kwargs):
        self.application.container.register(cls, *args, **kwargs)
        self.application.container.resolve(cls)

    def init(self):
        self.application.init()

    def registerComponent(self, cls, *args, **kwargs):
        self.application.container.register(cls, *args, **kwargs)

    def getBeans(self) -> dict:
        return self.application.context.instances

    def getComponents(self) -> dict:
        return self.application.context.getComponentDict()

    def getComponent(self, cls) -> ComponentWrapper:
        return self.application.componentContainer.getComponent(cls)

    def runComponent(self, cls):
        w = self.getComponent(cls)
        w.init()
        return w.run()

    def initAndRunAllComponents(self):
        self.application.componentContainer.initComponents()
        self.application.componentContainer.runComponents()

    def initAllComponents(self):
        self.application.componentContainer.initComponents()

    def runAllComponents(self):
        self.application.componentContainer.runComponents()
