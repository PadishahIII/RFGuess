from abc import abstractmethod

from Context.Context import Context


class ApplicationConfig:
    @abstractmethod
    def applicationConfig(self, ctx: Context):
        pass


class DefaultApplicationConfig(ApplicationConfig):
    def applicationConfig(self, ctx: Context):
        pass
