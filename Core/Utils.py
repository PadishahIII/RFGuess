import importlib
import inspect
import os
import pkgutil

beanClassList = list()
autowireClassNameList = list()
componentClassList = list()


class DecoratorUnit:
    def __init__(self, packageName: str = "", moduleName: str = '', className: str = '', funcName: str = '',
                 funcObj=None):
        self.packageName = packageName
        self.moduleName = moduleName
        self.className = className
        self.funcName = funcName
        self.funcObj = funcObj


def addAutoWireUnit(f):
    if not isinstance(f, type(scan_package)):
        raise Exception(f"Invail type {type(f)}, must be {type(scan_package())}")
    if not f.__qualname__ or len(f.__qualname__) <= 0:
        raise Exception(f"Error __qualname__ is invaild: {f.__qualname__}")
    name = f.__qualname__
    packageName = ""
    moduleName = ""
    className = ""
    funcName = ""
    ml = f.__module__.split(".")
    mll = [x for x in ml if x and len(x) > 0]
    if len(mll) <= 1:
        raise Exception(f"Error module name {f.__module__}")
    else:
        packageName = mll[-2]
        moduleName = mll[-1]

    l = name.split(".")
    ll = [x for x in l if x and len(x) > 0]
    if len(ll) <= 1:
        raise Exception(f"Error function {f} is not a property")
    else:
        className = ll[-2]
        funcName = ll[-1]
    unit = DecoratorUnit(packageName, moduleName, className, funcName, f)
    autowireClassNameList.append(unit)


def scan_package(package_name):
    package = __import__(package_name, fromlist=[""])

    for importer, modname, ispkg in pkgutil.walk_packages(
            path=package.__path__, prefix=package.__name__ + ".", onerror=lambda x: None
    ):
        module = __import__(modname, fromlist=[""])

        members = inspect.getmembers(module)
        print(f"members:\n{members}")
        for name, obj in members:
            if inspect.isclass(obj):
                class_decorators = []
                member_decorators = {}

                for decorator in obj.__dict__.get("__decorators__", []):
                    if inspect.isclass(decorator):
                        class_decorators.append(decorator.__name__)
                    elif inspect.isfunction(decorator):
                        member_decorators[decorator.__name__] = []

                for name, member in inspect.getmembers(obj):
                    if inspect.isfunction(member) and name != "__init__":
                        for decorator in member.__dict__.get("__decorators__", []):
                            if inspect.isfunction(decorator):
                                member_decorators[member.__name__].append(
                                    decorator.__name__
                                )

                # print(f"Class: {obj.__name__}")
                # print(f"Class decorators: {class_decorators}")
                # print(f"Member decorators: {member_decorators}")


def importModuleFromPackage(directory, packages: list):
    # directory = "."
    # directoryList = ["Components", "Component", "Configs", "Config"]
    directoryList = packages

    existedDirList = [d for d in os.listdir(directory) if d in directoryList]

    for d in existedDirList:

        moduleFiles: str = [f for f in os.listdir(d) if f.endswith(".py")]
        for moduleFile in moduleFiles:
            if moduleFile.startswith("__init__"):
                continue
            moduleName = moduleFile[:-3]
            module = importlib.import_module(f"{d}.{moduleName}")
