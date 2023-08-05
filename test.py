import json

from sklearn.ensemble import RandomForestClassifier

import Parser.CommonParsers
import Parser.PasswordParsers
from Classifiers import DTTrainner, RFTrainner
# from PasswordParser import *
from Classifiers.DTTrainner import *
from Classifiers._RFTest import RFTest
from Classifiers._TrainnersTest import DTTrainnerTest
from Core.Application import ApplicationWrapper
from Generators.DatasetGenerator import DatasetGenerator
from Generators.DictionaryGenerator import DictionaryGenerator
from Parser.PIIParsers import *
from Parser.PasswordParsers import *


def TrainTest():
    s = "qwe123!@3"
    p = Password(s)
    vectors = Utils.parseStandardVectorByPassword(p)
    labels = Utils.getLabelByPassword(p)


def modelTest():
    s = "qwe123!@#<>?"
    p = Password(s)
    vectors = Utils.parseStandardVectorByPassword(p)
    labels = Utils.getLabelByPassword(p)
    print(f"vectors:{len(vectors)}\n\nlabels:({len(labels)})\n")
    arr = np.array(vectors)
    arrLabel = np.array(labels)
    print(f"feature vector:({arr.shape})\n{arr}")
    print(f"label vector:({arrLabel.shape})\n{arrLabel}")
    # dt = DTTrainner(vectors, labels)
    # dt.train()
    # print(f"classify res:{dt.classify(p.datagramList[0])}")
    # print(json.dumps(p.datagramList[0]._tojson(), indent=2))
    # dt.exportTree()
    rf = RFTrainner.RFTrainner(vectors, labels)
    rf.train()
    # print(f"classify res:{rf.classify(p.datagramList[5])}")
    # print(json.dumps(p.datagramList[5]._tojson(), indent=2))
    s = "a"
    a_vector = Utils.parseStandardVectorByStr(s)
    print(f"classify res:{s}{rf.classifyVector(a_vector)}")


def preprocessTest():
    s = "qwe123"
    p = Password(s)
    vectors = Utils.parseStandardVectorByPassword(p)
    labels = Utils.getLabelByPassword(p)
    trainer = DTTrainner(vectors, labels)
    res = trainer.normalizeVector(vectors)
    # print(res)


def parserTest():
    cp = CharacterParser()
    kp = KeyboardParser()
    lp = LabelParser()
    s = "asdf123!@#"
    sl = lp.encodeStr(s)
    print(f"encode {s}:\n{sl}\ndecode :\n{lp.decodeList(sl)}")
    # print(kp.map)
    # print(list(x.getTuple() for x in kp.parseStr(r"a1qaasd{}|!@#")))


def passwordParserTest():
    password = "qwER12!@?"
    p = Password(password)
    jo = json.dumps(p._tojson(), indent=2)
    # print(jo)


def UtilsTest():
    s = "qwe123*()ads456!@#"
    # s = "qwER12!@?"
    # segList = Utils.parseSegment(s)
    # sl = Utils.getSegmentStrList(segList, s)
    # print(sl)
    # p = Password(s)
    # for i in range(0, len(s)):
    #     offset, segIndex = p.segmentOffset(i)
    #     print(f"i:{i} {s[i]} offset:{offset} {sl[segIndex]}")
    ss = "qwe123"
    print(Utils.parseStandardVectorByStr(ss))


def TransformTest():
    s = "qwe123"
    p = Password(s)
    vectors = Utils.parseStandardVectorByPassword(p)
    labels = Utils.getLabelByPassword(p)
    print(f"vectors:{len(vectors)}\n{vectors}\nlabels:({len(labels)})\n{labels}")


# def scanTest():
#     # scan_package("Components")
#     module = __import__("Components.Components", fromlist=[''])
#     members = inspect.getmembers(sys.modules['Components.Components'])
#     cls_ = Components.Test.Test
#     d = cls_.__dict__
#     members_s = inspect.getmembers_static(module)
#     # members_str = json.dumps(members,indent=2)
#     # members_sstr = json.dumps(members_s,indent=2)
#     # print(f"members:\n{members_str}")
#     # print(f"members static:\n{members_sstr}")
#     l = list()
#     for tu in members:
#         name = tu[0]
#         l.append(name)
#         if inspect.isclass(tu[1]):
#             print("!!!!!" + name)
#             print(tu[1])
#             if name == "Components":
#                 cls = tu[1]
#                 print(cls.__decorators__)
#     print(l)


def decoratorTest():
    module = __import__("Components.Components")


def applicationTest():
    s = "qwe123!@#<>?"
    p = Password(s)
    vectors = Utils.parseStandardVectorByPassword(p)
    labels = Utils.getLabelByPassword(p)
    print(f"vectors:{len(vectors)}\n\nlabels:({len(labels)})\n")
    arr = np.array(vectors)
    arrLabel = np.array(labels)
    print(f"feature vector:({arr.shape})\n{arr}")
    print(f"label vector:({arrLabel.shape})\n{arrLabel}")

    app = ApplicationWrapper()
    app.setComponentPackages(["Classifiers", ])
    app.addBean(preprocessing.MinMaxScaler)
    app.addBean(Parser.PasswordParsers.LabelParser)
    app.addBean(Parser.CommonParsers.LabelParser)
    app.addBean(Parser.PasswordParsers.LabelParser)
    app.addBean(RandomForestClassifier, n_estimators=30, criterion="gini")
    app.addBean(tree.DecisionTreeClassifier)

    app.registerComponent(DTTrainnerTest, vectors, labels)
    app.registerComponent(RFTest, vectors, labels)

    app.init()

    DTtrainner = app.getComponent(DTTrainnerTest)
    DTtrainner.init()
    DTtrainner.run()
    print(DTtrainner.classifyVector("q"))
    print(DTtrainner.classifyVector("a111"))
    print(DTtrainner.classifyVector("^&*(tyuiouytyu"))
    print(DTtrainner.classifyVector("^&*(tya111111111"))

    RFtrainner = app.getComponent(RFTest)
    RFtrainner.init()
    RFtrainner.run()
    print(RFtrainner.classifyVector("sdf"))
    print(RFtrainner.classifyVector("uio^&*"))
    print(RFtrainner.classifyVector("^&*hvbnvbnm"))


def generatorTest():
    app = ApplicationWrapper()
    app.setComponentPackages(["Generators", "Classifiers"])

    app.addBean(preprocessing.MinMaxScaler)
    app.addBean(Parser.CommonParsers.LabelParser)
    app.addBean(RandomForestClassifier, n_estimators=30, criterion="gini")
    app.addBean(tree.DecisionTreeClassifier)

    app.registerComponent(DatasetGenerator, r"D:\Files\WebPentestFiles&Books\Papers\datasets\rockyou.txt\rockyou.txt",
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


def piiParserTest():
    name = "abcdefg12345"
    a1 = "beg4"
    a2 = "ac4"
    a3 = "bg5"
    a4 = name
    a5 = "aeg5"
    a6 = "at5"
    a7 = "ag5t"

    pii = BasicTypes.PII(account="user123!@#",
                         name="yhangzhongjie",
                         firstName="yhang",
                         givenName="zhong jie",
                         birthday="19820607",
                         phoneNum="13222245678",
                         email="3501111asd11@qq.com",
                         idcardNum="1213213213")
    parser = PIIFullTagParser(pii,nameFuzz=True)
    parser.parseTag()
    tagContainer: PIITagContainer = parser.getTagContainer()
    tagList: typing.List[Tag] = tagContainer.getTagList()
    i = 1
    for tag in tagList:
        print(f"Tag id:{i}")
        print(f"\tType:{str(tag.piitype.__class__)+str(tag.piitype.name)}")
        print(f"\tValue:{tag.piitype.value}")
        print(f"\tString:{tag.s}")
        print("")
        i += 1

    # app.registerComponent(RFTrainner, features, labels)


# parserTest()
# passwordParserTest()
# UtilsTest()
# TransformTest()
# modelTest()
# preprocessTest()
# scanTest()
# decoratorTest()
# print(beanList)
# applicationTest()
# generatorTest()
piiParserTest()
