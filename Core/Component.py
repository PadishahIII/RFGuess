from abc import ABC, abstractmethod


# from Context.Context import Context

class AbstractComponent(ABC):
    # @abstractmethod
    # def getContext(self):
    #     pass
    #
    # @abstractmethod
    # def setContext(self, ctx):
    #     pass

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def run(self):
        pass

    # @abstractmethod
    # @property
    # def context(self):
    #     pass

from Context.Context import BasicContext
class BasicComponent(AbstractComponent,BasicContext):
    def __init__(self):
        super().__init__()
        # self._ctx = None

    # def getContext(self):
    #     return self._ctx
    #
    # def setContext(self, ctx):
    #     self._ctx = ctx

    def init(self):
        print("init")

    def run(self):
        print("run")

    # @property
    # def context(self):
    #     return self.context
    #
    # @context.setter
    # def context(self, ctx: Context):
    #     self.context = ctx
