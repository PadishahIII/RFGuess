# import PasswordParser
import numpy as np
from sklearn import preprocessing
from sklearn import tree

import Parser.PasswordParsers
from Commons import Utils
from Core.Component import AbstractComponent
from Core.Decorators import Component, Autowired


# @Component
class DTTrainnerTest(AbstractComponent):
    def __init__(self, feature: np.array=None, label: np.array=None) -> None:
        # def __init__(self) -> None:
        self._minMaxScaler = None
        # self._minMaxScaler = preprocessing.MinMaxScaler()
        self._lp: Parser.PasswordParsers.LabelParser = None
        # self._lp = Parser.PasswordParsers.LabelParser()
        self._feature = feature
        self._label = label
        # Classifier Config
        self._tree = None
        # self._tree = tree.DecisionTreeClassifier(criterion="gini", splitter="best")
        # Trainned Classifier
        self._clf = None

    # @property
    # def _minMaxScaler(self):
    #     return self._minMaxScaler

    # @_minMaxScaler.setter
    # @Autowired
    def minMaxScaler(self, s: preprocessing.MinMaxScaler):
        self._minMaxScaler = s

    # @property
    # def _lp(self):
    #     return self._lp

    # @_lp.setter
    # @Autowired
    def lp(self, lp: Parser.PasswordParsers.LabelParser):
        if not isinstance(lp, Parser.PasswordParsers.LabelParser):
            raise Exception(
                f"param type error: expected:{Parser.PasswordParsers.LabelParser} given:{lp.__class__}"
            )
        self._lp = lp

    # @property
    # def _tree(self):
    #     return self._tree

    # @_tree.setter
    # @Autowired
    def tree(self, t: tree.DecisionTreeClassifier):
        self._tree = t

    def classifyD(self, datagram: Parser.PasswordParsers.Datagram) -> str:
        arr: np.ndarray = self._classify(datagram)
        label = int(arr.astype(int)[0])
        labelCh = self._lp.decodeCh(label)
        return labelCh

    def classify(self, s: str) -> str:
        d = Utils.parseStrToDatagram(s)
        labelCh = self.classifyD(d)
        return s + labelCh

    def _classify(self, datagram: Parser.PasswordParsers.Datagram):
        feature = np.array(Utils.parseStandardVector(datagram))
        feature = np.array([feature])
        return self._clf.predict(feature)

    def exportTree(self):
        print(tree.export_text(self._clf))
        # data = tree.export_graphviz(self._clf, out_file="Output/tree.png")
        # graph = graphviz.Source(data)
        # graph.render("test")

    # Train the Classifier
    def train(self):
        self._train()

    # Train the Classifier
    def _train(self):
        self._clf = self._tree.fit(self._feature, self._label)

    # Scaling features into [-1,1] range
    # If using CART DT, it seems there is no need to normalize features
    def normalizeVector(self, vector: np.array) -> np.array:
        norVector: np.array = self._minMaxScaler.fit_transform(vector)
        return norVector

    def init(self):
        pass

    def run(self):
        self.train()
