import os

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from Commons.Modes import Singleton
from Parser import Config
from Parser.PIIDataTypes import *


class PIIRFTrainner(Singleton):
    def __init__(self, features: list = None, labels: list = None) -> None:
        super().__init__()
        self._feature = features
        self._label = labels
        self._tree = RandomForestClassifier(n_estimators=Config.RFParams.n_estimators,
                                            criterion=Config.RFParams.criterion,
                                            min_samples_leaf=Config.RFParams.min_samples_leaf,
                                            max_features=Config.RFParams.max_features)
        self._clf = None

    @classmethod
    def loadFromFile(cls, clfPath):
        if not os.path.exists(clfPath):
            raise PIIRFTrainnerException(f"Error: invalid classifier path: {clfPath}")
        clf = joblib.load(clfPath)
        t = PIIRFTrainner.getInstance()
        t.setClf(clf)
        return t

    def init(self):
        pass

    def run(self):
        self.train()

    def train(self):
        self._train()

    def _classify(self, vector: list[int]) -> int:
        """
        Input a 26-dim vector(namely a `PIIDatagram`), output the classifying result

        """
        feature = np.array(vector)
        feature = np.array([feature])
        label_r = self._clf.predict(feature)
        label = int(label_r.astype(int)[0])
        return label

    def _classifyProba(self, vector: list[int], n: int) -> list[int]:
        """
        Input a 26-dim vector(namely a `PIIDatagram`), output the classifying result at top-n probability
        Args:
            vector (list[int]): 26-dim
            n (int): get top-n probability classes

        Returns:
            list of top-n probability classes in descending order

        """
        feature = np.array(vector)
        feature = np.array([feature])
        proba = self._clf.predict_proba(feature)
        ds = self.getSortedClassesList(proba, n)
        labelList = list(map(lambda x: x[0], ds))
        # label = int(label_r.astype(int)[0])
        return labelList

    def _classifyToProbaDict(self, vector: list[int]) -> dict[int, float]:
        """
        Input a 26-dim vector(namely a `PIIDatagram`), output all classes with corresponding probability
        Args:
            vector (list[int]): 26-dim

        Returns:
            dict[int, float]: all classes to corresponding probability in descending order

        """
        feature = np.array(vector)
        feature = np.array([feature])
        proba = self._clf.predict_proba(feature)
        ds = self.getSortedClassesList(proba, len(self._clf.classes_))
        d: dict[int, float] = {x[0]: x[1] for x in ds}
        return d

    def getSortedClassesList(self, proba: tuple[tuple], n: int) -> list[tuple[int, float]]:
        """
        Get the top-n classes with probability
        Args:
            proba: result of `predict_proba` in format ((0.4,0.6),)
            n: slice number

        Returns:
            ((class_label, probability),)

        """
        d = zip(self._clf.classes_[:n], proba[0][:n])
        ds = sorted(d, key=lambda x: x[1], reverse=True)
        return ds

    def classifyPIIDatagram(self, datagram: PIIDatagram) -> int:
        vector = datagram._tovector()
        return self._classify(vector)

    def classifyPIIDatagramProba(self, datagram: PIIDatagram, n) -> list[int]:
        """
        Input a `PIIDatagram`, output the classifying result at top-n probability

        Returns:
            list of top-n probability classes in descending order

        """
        vector = datagram._tovector()
        return self._classifyProba(vector, n)

    def classifyPIIDatagramToProbaDict(self, datagram: PIIDatagram) -> dict[int, float]:
        """
        Input a `PIIDatagram`, output all classes with corresponding probability

        Returns:
            all classes with corresponding probability in descending order

        """
        vector = datagram._tovector()
        return self._classifyToProbaDict(vector)

    def _train(self):
        self._clf = self._tree.fit(self._feature, self._label)

    def getClf(self):
        return self._clf

    def setClf(self, clf):
        self._clf = clf


class PIIRFTrainnerException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
