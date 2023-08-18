import numpy as np
from sklearn.ensemble import RandomForestClassifier

from Commons.Modes import Singleton


class PIIRFTrainner(Singleton):
    def __init__(self, features: list = None, labels: list = None) -> None:
        super().__init__()
        self._feature = features
        self._label = labels
        self._tree = RandomForestClassifier(n_estimators=30, criterion="gini", min_samples_leaf=10)
        self._clf = None

    def init(self):
        pass

    def run(self):
        self.train()

    def train(self):
        self._train()

    def classify(self, vector: list[int]) -> int:
        """
        Input a 26-dim vector(namely a PIISection), output the classifying result

        """
        feature = np.array(vector)
        feature = np.array([feature])
        label_r = self._clf.predict(feature)
        label = int(label_r.astype(int)[0])
        return label

    def _train(self):
        self._clf = self._tree.fit(self._feature, self._label)

    def getClf(self):
        return self._clf

    def setClf(self, clf):
        self._clf = clf
