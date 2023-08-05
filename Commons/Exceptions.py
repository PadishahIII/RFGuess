class ParseException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class InitializationException(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
class ContextException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class ApplicationException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class GeneratorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class PIIParserException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)