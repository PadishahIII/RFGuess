import logging
import os

from Parser.GeneralPIIParsers import *

logger = logging.getLogger("Generator")
logger.setLevel(logging.CRITICAL)

class GeneralPasswordGenerator(Singleton):
    """
    Input PII data and patterns, generate password guess
    Fuzz PII fields to generate guesses more accurately
    Notes:
        If a pattern contains section which don't have corresponding PII data, the pattern would be discarded

    Examples:
        generator: GeneralPasswordGenerator = GeneralPasswordGenerator.getInstance(
            patternFile="../patterns_general.txt",
        )
        generator.init()
        generator.generateForPII(outputFile="../passwords_general.txt",
                                 pii=pii,
                                 nameFuzz=True)
        generator.generateForPII(outputFile="../passwords_general_2.txt",
                                 pii=pii2,
                                 nameFuzz=True)

    """

    def __init__(self, patternFile: str) -> None:
        super().__init__()
        self.patternFile = patternFile

        self.initPatterns: list[GeneralPIIDatagram] = list()  # patters without eliminate
        self.patternStrList: list[str] = list()

    @classmethod
    def getInstance(cls, patternFile: str):
        return super().getInstance(patternFile)

    def init(self):
        self.guesses:list[str] = list()
        self.datagramFactory: GeneralPIIDatagramFactory = GeneralPIIDatagramFactory.getInstance()
        self.sectionFactory: GeneralPIISectionFactory = GeneralPIISectionFactory.getInstance()
        print(f"Load pattern file: {self.patternFile}")
        self.readPatternsAsDatagram()
        print(f"Read patterns: {len(self.initPatterns)}\n")

    def generateForPII(self, pii: PII, outputFile: str, nameFuzz: bool = False):
        """Generate guesses for certain PII

        Args:
            pii: PII data
            outputFile: guesses output path, None for no save
            nameFuzz: if toggle name fuzzer or not

        """
        logger.info(f"Preparing PII tag container...")
        self.pii = pii
        self.guesses: list[str] = list()
        self.patterns: list[GeneralPIIDatagram] = list()
        self.outputFile = outputFile
        self.piiTagContainer: PIITagContainer = PIITagContainer(pii=self.pii, nameFuzz=nameFuzz)
        self.piiTagContainer.parse()
        self.tagDict: dict[Enum, list[str]] = self.piiTagContainer.getTagDict()  # specified pii type to string

        self.eliminatePatternDatagrams()
        logger.info(
            f"Number of patterns after eliminating: {len(self.patterns)}, remove: {len(self.initPatterns) - len(self.patterns)}")

        logger.info(f"Start generating guesses...")
        self.generateALlGuesses()
        primaryLen = len(self.guesses)
        self.guesses = self.eliminateDuplicateGuess()
        newLen = len(self.guesses)
        logger.info(f"Generating complete, number of guesses: {primaryLen}")
        logger.info(f"Eliminate guesses: remove {primaryLen - newLen} duplicates, final guess number: {newLen}")
        if self.outputFile != None and len(self.outputFile) >0:
            self.save()
        logger.info(f"Complete!\nCount:{newLen}\nSaved to {self.outputFile}\n")

    def readPatternsAsDatagram(self):
        """
        Read all patterns and parse into datagram

        """
        if not os.path.exists(self.patternFile):
            raise PasswordGuessGeneratorException(f"Error: file {self.patternFile} not exist")
        with open(self.patternFile, "r") as f:
            line = f.readline()
            while line:
                line = line.strip()
                if line == '':
                    line = f.readline()
                    continue
                try:
                    dg: GeneralPIIDatagram = self.datagramFactory.createFromStr(line)
                    self.initPatterns.append(dg)
                except Exception as e:
                    raise PasswordGuessGeneratorException(
                        f"Exception occur when parsing pattern file, Original exception is {e}")
                line = f.readline()

    def eliminatePatternDatagrams(self):
        """
        Eliminate patterns that do not have corresponding fields in PII data

        """
        newPatterns: list[GeneralPIIDatagram] = list()
        for dg in self.initPatterns:
            sectionList: list[GeneralPIISection] = dg.sectionList
            accept: bool = True
            for section in sectionList:
                if section.isPII:
                    piiSection: PIISection = section.vector
                    specifiedType: Enum = piiSection.value
                    if specifiedType not in self.tagDict.keys():
                        accept = False
                        break
            if accept:
                newPatterns.append(dg)
        self.patterns = newPatterns

    def generateGuessFromPatternStr(self, patternStr: str) -> list[str]:
        """Input a pattern string and output all guesses generated

        """
        dg: GeneralPIIDatagram = self.datagramFactory.createFromStr(patternStr)
        return self.generateGuessFromPatternDatagram(dg)

    def generateGuessFromPatternDatagram(self, patternDg: GeneralPIIDatagram) -> list[str]:
        """Input a pattern datagram and output all guesses generated


        Returns:
            list : list of guesses
        """
        mixList = self.transformDatagramToMixlist(patternDg)
        permutations: list[list] = self.generate_permutations(mixList)
        guessList: list[str] = list()
        for permutation in permutations:
            guessList.append(''.join(permutation))
        return guessList

    def transformDatagramToMixlist(self, patternDg: GeneralPIIDatagram) -> list:
        """Transform a datagram into a list mixed with str or list[str]
        If there is no pii data corresponding, the pattern should be discarded and returen empty list
        Returns:
            list : list mixed with str or list[str]
        """
        mixList = list()
        sectionList: list[GeneralPIISection] = patternDg.sectionList
        for section in sectionList:
            if section.isPII:
                piiSection: PIISection = section.vector
                specifiedType: Enum = piiSection.value
                if specifiedType not in self.tagDict.keys():
                    # pii data not exist, ignore this pattern
                    return list()
                piiStrList: list[str] = self.tagDict.get(specifiedType)
                mixList.append(piiStrList)
            else:
                charSection: CharacterSection = section.vector
                ch: str = charSection.ch
                mixList.append(ch)
        return mixList

    def generateALlGuesses(self):
        """
        Generate all guesses from pattern list

        """
        for dg in self.patterns:
            guesses: list[str] = self.generateGuessFromPatternDatagram(dg)
            self.guesses += guesses

    def eliminateDuplicateGuess(self) -> list[str]:
        """Eliminate duplicated guesses (in string format)

        """
        return list(set(self.guesses))

    def generate_permutations(self, mixed_list) -> list[list]:
        """
        Input a list mixed with str and list[str], like ['a', ['1', '2'], 'b', ['c', 'd'], 'e'], output all permutations

        Examples:
            permutations = generate_permutations(mixed_list)
            for permutation in permutations:
                print(''.join(permutation))


        Args:
            mixed_list: list mixed with str or list[str]

        Returns:
            list[list[str]]

        """
        if len(mixed_list) == 0:
            return [[]]

        first_element = mixed_list[0]
        remaining_elements = mixed_list[1:]

        permutations = []

        for permutation in self.generate_permutations(remaining_elements):
            if isinstance(first_element, str):
                permutations.append([first_element] + permutation)
            elif isinstance(first_element, list):
                for element in first_element:
                    permutations.append([element] + permutation)

        return permutations

    def save(self):
        with open(self.outputFile, "w") as f:
            for p in self.guesses:
                f.write(f"{p}\n")


class PasswordGuessGeneratorException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
