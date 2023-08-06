from unittest import TestCase

from sklearn.ensemble import RandomForestClassifier

import Parser.CommonParsers
import Parser.PasswordParsers
from Classifiers import RFTrainner
# from PasswordParser import *
from Classifiers.DTTrainner import *
from Core.Application import ApplicationWrapper
from Generators.DatasetGenerator import DatasetGenerator
from Generators.DictionaryGenerator import DictionaryGenerator
from Parser.PIIParsers import *
from Parser.PasswordParsers import *


class TestRFTrainner(TestCase):
    def test_init(self):
        self.fail()

    def test_run(self):
        app = ApplicationWrapper()
        app.setComponentPackages(["Generators", "Classifiers"])

        app.addBean(preprocessing.MinMaxScaler)
        app.addBean(Parser.CommonParsers.LabelParser)
        app.addBean(RandomForestClassifier, n_estimators=30, criterion="gini")
        app.addBean(tree.DecisionTreeClassifier)

        app.registerComponent(DatasetGenerator,
                              r"D:\Files\WebPentestFiles&Books\Papers\datasets\rockyou.txt\rockyou.txt",
                              saveName="dataset.txt")
        app.registerComponent(RFTrainner)
        seeds = ["qwe", "admi", "alice123", "bob1999"]
        app.registerComponent(DictionaryGenerator, seedList=seeds)

        app.init()

        gen = app.getComponent(DatasetGenerator)
        gen.init()
        # print(gen.context.getBean(preprocessing.MinMaxScaler))
        # exit(0)
        features, labels = gen.obj.getDataset()

        print(f"feature number:{len(features)}\nlabel number:{len(labels)}")

        trainer = app.getComponent(RFTrainner.RFTrainner)
        trainer.obj._feature = features
        trainer.obj._label = labels
        trainer.init()
        trainer.run()
        print(f"{trainer.classify('qwer')}")
        print(f"{trainer.classify('1234')}")
        print(f"{trainer.classify('admi')}")
        print(f"{trainer.classify('admi')}")
        print(f"{trainer.classify('admi')}")
        print(f"{trainer.classify('alice0102')}")

        dicGen = app.getComponent(DictionaryGenerator)
        dicGen.init()
        dicGen.run()

    def test_set_lp(self):
        self.fail()

    def test_set_tree(self):
        self.fail()

    def test_classify(self):
        self.fail()

    def test_classify_vector(self):
        self.fail()

    def test_classify_datagram(self):
        self.fail()

    def test__classify_datagram(self):
        self.fail()

    def test_train(self):
        self.fail()

    def test__train(self):
        self.fail()
