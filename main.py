from sklearn.ensemble import RandomForestClassifier

from Classifiers import RFTrainner
# from Parser.PasswordParsers import *
import Parser
from Classifiers.DTTrainner import *
from Core.Application import ApplicationWrapper
from Generators.DatasetGenerator import DatasetGenerator
from Generators.DictionaryGenerator import DictionaryGenerator

if __name__ == '__main__':
    app = ApplicationWrapper()
    app.setComponentPackages(["Generators", "Classifiers"])

    app.addBean(preprocessing.MinMaxScaler)
    app.addBean(Parser.CommonParsers.LabelParser)
    app.addBean(RandomForestClassifier, n_estimators=30, criterion="gini",min_samples_leaf=10)
    app.addBean(tree.DecisionTreeClassifier)

    app.registerComponent(DatasetGenerator, r"D:\Files\WebPentestFiles&Books\Papers\datasets\rockyou.txt\rockyou.txt",
                          saveName="dataset.txt")
    app.registerComponent(RFTrainner)
    seeds = ["qwe", "admi", "alice123", "bob1999"]
    app.registerComponent(DictionaryGenerator, seedList=seeds)

    app.init()

    gen = app.getComponent(DatasetGenerator)
    gen.init()
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
