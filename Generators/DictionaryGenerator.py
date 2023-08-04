from Classifiers.RFTrainner import RFTrainner
from Core.Component import BasicComponent
from Core.Decorators import Autowired, Component


@Component
class DictionaryGenerator(BasicComponent):

    def __init__(self, seedList: list = list(), saveFile: str = "passwordDic.txt") -> None:
        super().__init__()
        self._model: RFTrainner = None
        self._plist = list()
        self._seeds = seedList
        self._saveFile = saveFile
        self._file = None
        self._limit = 100
        self._count = 0
        self._ctx = super().context

    @Autowired
    def setModel(self, m: RFTrainner):
        self._model = m

    def run(self):
        for seed in self._seeds:
            p: str = seed
            i = 0
            while not p.__contains__("<End") and i < self._limit:
                p = self._model.classify(p)
                i += 1
            pp = p.replace("<EndSymbol>", "")
            self._plist.append(pp)
            self.save(pp)
            self._count += 1
        self.close()

    def init(self):
        self._file = open(self._saveFile, "w+", encoding="utf-8", errors="ignore")
        if self._file == None:
            raise Exception(f"Error: Failed to open file {self._saveFile}")

    def close(self):
        self._file.close()
        print(f"dictionary generated to {self._saveFile}, total: {self._count}")

    def save(self, p: str):
        self._file.write(p)
        self._file.write("\n")
