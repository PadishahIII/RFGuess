from Context.Context import Context


# read or write instances to context
class Container:
    def __init__(self, context: Context):
        self.dependencies = {}
        self.context = context

    def register(self, cls, *args, **kwargs):
        tu = self.getDependency(cls)
        if tu == None:
            self.dependencies[self.hash(cls)] = (args, kwargs)


    def resolve(self, cls):
        obj = self.context.getExistingInstance(cls)
        if obj != None:
            return obj
        tu = self.getDependency(cls)
        if tu == None:
            raise Exception(f"No registered dependency found for {cls.__name__}")
        args = tu[0]
        kwargs = tu[1]
        dependencies = [self.resolve(arg) if isinstance(arg, type) else arg for arg in args]
        obj = cls(*dependencies, **kwargs)
        self.context.storeInstance(cls, obj)
        return obj

    def getDependency(self, cls):
        h = self.hash(cls)
        if h not in self.dependencies:
            return None
        return self.dependencies[h]

    def hash(self, cls):
        return id(cls)
