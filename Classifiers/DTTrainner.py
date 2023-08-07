# import PasswordParser
import numpy as np
from sklearn import preprocessing
from sklearn import tree
from Core.Decorators import Component
from Commons import Utils
import Parser.PasswordParsers

class DTTrainner:
    def __init__(self, feature: np.array=None, label: np.array=None) -> None:
        self._minMaxScaler = preprocessing.MinMaxScaler()
        self._lp = Parser.PasswordParsers.LabelParser()
        self._feature = feature
        self._label = label
        # Classifier Config
        self._tree = tree.DecisionTreeClassifier(criterion="gini", splitter="best")
        # Trainned Classifier
        self._clf = None

    def classify(self, datagram: Parser.PasswordParsers.Datagram) -> str:
        arr: np.ndarray = self._classify(datagram)
        label = int(arr.astype(int)[0])
        labelCh = self._lp.decodeCh(label)
        return labelCh

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
