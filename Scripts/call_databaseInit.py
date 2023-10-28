from unittest import TestCase

from Scripts import databaseInit


class Test(TestCase):
    def test_load_dataset(self):
        pass
        # databaseInit.LoadDataset(r"E:\datasets\2014\2014.12-12306-13m-txt\12306dataset.txt", start=0, limit=-1,
        #                          clear=True, update=False)

    def test_query(self):
        queryMethods = databaseInit.PIIUnitQueryMethods()

        units = queryMethods.QueryWithLimit(offset=0, limit=2)
        for u in units:
            print(str(u))

    def test_representation(self):
        pwStr = "qwe123ryhang0607yuiyzj123wqer!@#"
        pwStr2 = "qwer4y3245"
        rep = "gASVkgIAAAAAAACMEVBhcnNlci5QSUlQYXJzZXJzlIwRUElJUmVwcmVzZW50YXRpb26Uk5QpgZR9lCiMDXBpaVZlY3Rvckxpc3SUXZQoaACMCVBJSVZlY3RvcpSTlCmBlH2UKIwDc3RylIwDcXdllIwHcGlpdHlwZZSMCGJ1aWx0aW5zlIwHZ2V0YXR0cpSTlIwSQ29tbW9ucy5CYXNpY1R5cGVzlIwRUElJVHlwZS5CYXNlVHlwZXOUk5SMAUyUhpRSlIwIcGlpdmFsdWWUTVgbjANyb3eUSwCMA2NvbJRLAHViaAgpgZR9lChoC4wDMTIzlGgNaBBoE4wBRJSGlFKUaBdNQB9oGEsAaBlLAHViaAgpgZR9lChoC4wBcpRoDWgWaBdNWBtoGEsAaBlLAHViaAgpgZR9lChoC4wFeWhhbmeUaA1oEGgRjBBQSUlUeXBlLk5hbWVUeXBllJOUjApGYW1pbHlOYW1llIaUUpRoF0sDaBhLAGgZSwB1YmgIKYGUfZQoaAuMBDA2MDeUaA1oEGgRjBRQSUlUeXBlLkJpcnRoZGF5VHlwZZSTlIwERGF0ZZSGlFKUaBdLBGgYSwBoGUsAdWJoCCmBlH2UKGgLjAN5dWmUaA1oFmgXTVgbaBhLAGgZSwB1YmgIKYGUfZQoaAuMA3l6apRoDWgQaCeMCEFiYnJOYW1llIaUUpRoF0sCaBhLAGgZSwB1YmgIKYGUfZQoaAuMAzEyM5RoDWgfaBdNQB9oGEsAaBlLAHViaAgpgZR9lChoC4wEd3FlcpRoDWgWaBdNWBtoGEsAaBlLAHViaAgpgZR9lChoC4wDIUAjlGgNaBBoE4wBU5SGlFKUaBdNKCNoGEsAaBlLAHViZYwDbGVulEsKdWIu"
        rep2 = "gASVmQIAAAAAAACMEVBhcnNlci5QSUlQYXJzZXJzlIwRUElJUmVwcmVzZW50YXRpb26Uk5QpgZR9lCiMDXBpaVZlY3Rvckxpc3SUXZQoaACMCVBJSVZlY3RvcpSTlCmBlH2UKIwDc3RylIwDcXdllIwHcGlpdHlwZZSMCGJ1aWx0aW5zlIwHZ2V0YXR0cpSTlIwSQ29tbW9ucy5CYXNpY1R5cGVzlIwRUElJVHlwZS5CYXNlVHlwZXOUk5SMAUyUhpRSlIwIcGlpdmFsdWWUTVgbjANyb3eUSwCMA2NvbJRLAHViaAgpgZR9lChoC4wDMTIzlGgNaBBoE4wBRJSGlFKUaBdNQB9oGEsAaBlLAHViaAgpgZR9lChoC4wBcpRoDWgWaBdNWBtoGEsAaBlLAHViaAgpgZR9lChoC4wFeWhhbmeUaA1oEGgRjBBQSUlUeXBlLk5hbWVUeXBllJOUjApGYW1pbHlOYW1llIaUUpRoF0sDaBhLAGgZSwB1YmgIKYGUfZQoaAuMBDA2MDeUaA1oEGgRjBNQSUlUeXBlLkFjY291bnRUeXBllJOUjAxEaWdpdFNlZ21lbnSUhpRSlGgXSwNoGEsAaBlLAHViaAgpgZR9lChoC4wDeXVplGgNaBZoF01YG2gYSwBoGUsAdWJoCCmBlH2UKGgLjAN5emqUaA1oEGgnjAhBYmJyTmFtZZSGlFKUaBdLAmgYSwBoGUsAdWJoCCmBlH2UKGgLjAMxMjOUaA1oH2gXTUAfaBhLAGgZSwB1YmgIKYGUfZQoaAuMBHdxZXKUaA1oFmgXTVgbaBhLAGgZSwB1YmgIKYGUfZQoaAuMAyFAI5RoDWgQaBOMAVOUhpRSlGgXTSgjaBhLAGgZSwB1YmWMA2xlbpRLCnViLg=="
        hashStr = databaseInit.PwRepresentation.getHash(rep)

        pr = databaseInit.PwRepresentation(pwStr=pwStr, repStr=rep, )
        pr2 = databaseInit.PwRepresentation(pwStr=pwStr, repStr=rep2)
        pr3 = databaseInit.PwRepresentation(pwStr=pwStr2, repStr=rep)

        queryMethods = databaseInit.RepresentationMethods()
        # queryMethods.Insert(pr)
        queryMethods.Insert(pr2)
        queryMethods.Insert(pr3)
        return
        units = queryMethods.QueryAll()

        def displayList(units: list):
            for unit in units:
                print(str(unit))
            print("")

        print("QueryAll:")
        displayList(units)
        units = queryMethods.QueryWithPwStr(pwStr)
        print("QueryWithPwStr:")
        displayList(units)
        units = queryMethods.QueryWithWholeHash(databaseInit.PwRepresentation.getHash(pwStr + rep))
        print("QueryWithWholeHash:")
        displayList(units)
        units = queryMethods.QueryWithRepresentationHash(hashStr)
        print("QueryWithRepHash:")
        displayList(units)

    def test_frequency(self):
        queryMethods = databaseInit.RepresentationFrequencyMethods()
        units = queryMethods.QueryAllWithFrequencyDesc()
        for unit in units:
            print(str(unit))
