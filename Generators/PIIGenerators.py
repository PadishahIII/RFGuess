from Commons.Utils import translation, getEnumTypeFromInt
from Parser.PIIDataTypes import *

'''
Generators: use trained model to generate password guessing
'''


class PIIPatternGenerator:
    """PIIPatternGenerator
    Generate password patterns utilizing classifier

    Parse the result of classifier into `PIISection`
    """

    def __init__(self) -> None:
        super().__init__()
        fromList = [
            BasicTypes.PIIType.BaseTypes.Name.value,
            BasicTypes.PIIType.BaseTypes.Birthday.value,
            BasicTypes.PIIType.BaseTypes.Account.value,
            BasicTypes.PIIType.BaseTypes.Email.value,
            BasicTypes.PIIType.BaseTypes.PhoneNumber.value,
            BasicTypes.PIIType.BaseTypes.IdCardNumber.value,
        ]
        toList = [
            BasicTypes.PIIType.NameType,
            BasicTypes.PIIType.BirthdayType,
            BasicTypes.PIIType.AccountType,
            BasicTypes.PIIType.EmailPrefixType,
            BasicTypes.PIIType.PhoneNumberType,
            BasicTypes.PIIType.IdCardNumberType
        ]
        self.translation = translation.makeTrans(fromList, toList)

    def createSectionFromInt(self, i: int) -> PIISection:
        if i == 0:
            return PIISection(BasicTypes.PIIType.BaseTypes.BeginSymbol, 0)
        elif i < 0:
            return PIISection(BasicTypes.PIIType.BaseTypes.EndSymbol, 0)

        td = int(i // 1e3)
        if td > 0:
            typeValue = int(i // 1e3) * 1e3
            value = int(i % 1e3)
            if typeValue in self.translation.fromDict.keys():
                t: BasicTypes.PIIType = self.translation.translate(typeValue)
                enumCls = getEnumTypeFromInt(t, value)
            else:
                # LDS
                enumCls: BasicTypes.PIIType.BaseTypes = getEnumTypeFromInt(BasicTypes.PIIType.BaseTypes, typeValue)
            if enumCls is None:
                raise PIILabelException(f"Error: cannot create PIILabel, invalid pii value:{value} in {i}")
            return PIISection(enumCls, value)
        else:
            raise PIILabelException(f"Error: cannot create PIILabel, invalid Integer:{i}")
