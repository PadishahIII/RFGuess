import inspect

from Core.Utils import beanClassList, addAutoWireUnit, componentClassList


def Component(cls):
    if inspect.isclass(cls):
        componentClassList.append(cls)
    else:
        raise Exception(f"@Component can only decorate class, given {cls}:{type(cls)}")

    def wrapper(f):
        return f

    return wrapper(cls)


def Bean(cls):  # class
    if inspect.isclass(cls):
        beanClassList.append(cls)
    else:
        raise Exception("@Bean can only use to decorate class")

    def wrapper(f):  # class
        return f

    return wrapper(cls)


def Autowired(cls):
    addAutoWireUnit(cls)

    def wrapper(f):
        return f

    return wrapper(cls)
