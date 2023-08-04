import os

import Commons.Utils as Utils
import Parser
from Commons.Exceptions import GeneratorException
from Core.Component import BasicComponent
from Core.Decorators import Component, Autowired
from Parser.PasswordParsers import Password


# Read from file or generate from regulate
# password str => (vectors, labels)
@Component
class DatasetGenerator(BasicComponent):
    def __init__(self, f: str, start: int = 0, limit: int = 1e3, saveName="dataset.txt"):
        super().__init__()
        self.featureList = list()
        self.labelList = list()
        self.file = f
        self.start = start
        self.limit = int(limit)
        self._i = 0
        self.savePath = "."
        self.saveName = saveName
        self.charset = "1234567890-=!@#$%^&*()_+qwertyuiop[]\\QWERTYUIOP{}|asdfghjkl;'ASDFGHJKL:\"zxcvbnm,./ZXCVBNM<>?"

        self.characterParser = None
        self.keyboardParser = None


    @Autowired
    def setCharacterParser(self, cp: Parser.PasswordParsers.CharacterParser):
        self.characterParser = cp

    @Autowired
    def setKeyboardParser(self, kp: Parser.CommonParsers.KeyboardParser):
        self.keyboardParser = kp

    def getDataset(self) -> tuple:
        return (self.featureList, self.labelList)

    def init(self):
        print(f"Start to generate dataset...\nlocation: {self.file}\nlimitation: {self.limit}")
        self._build()

    def run(self):
        pass

    def save(self, plist: list):
        with open(os.path.join(self.savePath, self.saveName), "w", encoding="utf-8", errors="ignore") as f:
            f.write('\n'.join(plist))
        print(f"saved to {self.savePath + '/' + self.saveName}")

    def _build(self):
        if self.file == None or not os.path.exists(self.file):
            raise GeneratorException(f"{self.file} not exists")
        pl = self.readFromFile(self.file)
        for p in pl:
            if self._i > self.limit:
                break
            self.resolvePassword(p)
            self._i += 1
        print(f"Generate Finished. Total data number: {self._i}")
        self.save(pl)

    def resolvePassword(self, p: str):
        Parser.PasswordParsers.CONTEXT = self.context
        password = Password(p)
        # password.context = self.context
        vectors = Utils.parseStandardVectorByPassword(password)
        labels = Utils.getLabelByPassword(password)
        self.featureList += vectors
        self.labelList += labels

    def readFromFile(self, file: str) -> list:
        with open(file, "r", encoding="utf-8", errors="ignore") as f:
            for i in range(self.start):
                f.readline()
            l = list()
            for i in range(int(self.limit)):
                l.append(f.readline())
        ll = list()
        for w in l:
            if len(w) <= 0:
                continue
            ww = w.strip()
            www = ""
            for c in ww:
                if c in self.charset:
                    www += c
            if len(www) > 0:
                ll.append(www)

        return ll
