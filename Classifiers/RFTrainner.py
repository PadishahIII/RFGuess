import typing

import numpy as np
from sklearn.ensemble import RandomForestClassifier

from Commons import Utils
from Core.Component import BasicComponent
from Core.Decorators import Component, Autowired
from Parser import CommonParsers, PasswordParsers


@Component
class RFTrainner(BasicComponent):
    def __init__(self, features: np.array = None, labels: np.array = None) -> None:
        super().__init__()
        self._lp = None
        self._feature = features
        self._label = labels
        self._tree = None
        self._clf = None
        # self._ctx = super().context

    def init(self):
        pass

    def run(self):
        self.train()

    @Autowired
    def setLp(self, p: CommonParsers.LabelParser):
        self._lp = p

    @Autowired
    def setTree(self, t: RandomForestClassifier):
        self._tree = t

    def classify(self, s: str) -> str:
        d = Utils.parseStrToDatagram(s)
        labelCh = self.classifyDatagram(d)
        return s + labelCh

    def classifyVector(self, vector: typing.List[int]) -> str:
        feature = np.array(vector)
        feature = np.array([feature])
        label_r = self._clf.predict(feature)
        label = int(label_r.astype(int)[0])
        labelCh = self._lp.decodeCh(label)
        return labelCh

    def classifyDatagram(self, datagram: PasswordParsers.Datagram) -> str:
        arr: np.ndarray = self._classifyDatagram(datagram)
        label = int(arr.astype(int)[0])
        labelCh = self._lp.decodeCh(label)
        return labelCh

    def _classifyDatagram(self, datagram: PasswordParsers.Datagram):
        feature = np.array(Utils.parseStandardVector(datagram))
        feature = np.array([feature])
        return self._clf.predict(feature)

    def train(self):
        self._train()

    def _train(self):
        self._clf = self._tree.fit(self._feature, self._label)
