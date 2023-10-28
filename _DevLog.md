# Random Forest Password Guessing Model

## Overview

https://www.usenix.org/conference/usenixsecurity23/presentation/wang-ding-password-guessing

## Model Parameter
1. min_samples_leaf=10: given the length of passwords almost larger than 6, a password would generate 9~10 datagrams averagely, so the minimum datagram number of a leaf is set to 10
2. n_estimators=30: 30 decision trees
3. criterion='gini': CART decision tree
4. max_features=0.8: 80% features are selected randomly when splitting nodes 



## Tutorial for development
### Database manipulation and preprocess
There are two circumstances as for database-manipulation, one of which is about reading from the **primitive** database
(e.g. *PII* datatable) and the other is for intermediate databases (namely, datatables employed by algorithms, e.g. datatable
for representation frequency). Different classes are employed in each of circumstances. `Preprocessor` is defined for processing
raw dataset so it has many preprocess methods to format the dataset and eliminate duplicates. `DatabaseTransformer` is used as
the communication bridge between database and high-level algorithms, transformer would provide transformation methods to intermediates and
dataunits, and proxify the lower level data-manipulation classes.
1. `Preprocessor`: preprocessors are dedicated in **reading** from **primitive** databases and do some preprocessing like eliminate duplicate or check fields. You can reach such classes
in `Parsers` package. `BasicPreProcessor` is the ancestor class for all preprocessors deriving `FilePreProcessor` to read
dataset from file and `DatabasePreProcessor` to load data from certain database. One can write self-defined preprocessors
by extending one of the two basic preprocessors. There are some preprocessors ready to use in the password-guessing subject
such as `PIIPreprocessor` which reads PII data from primitive PII dataset and employ certain preprocess functions.
2. `DatabaseTranformer`: *transformer* usually serves as a proxy to the database-manipulation and also provide some transform
methods between raw database unit(which is poorly representative) and more dedicated unit type used in facade algorithms.
A transformer is bound to a certain *queryMethods*(derived from `BasicManipulateMethods` class) and usually includes an 
intermediate unit class to describe database unit in a more expressive way, some transform methods (*classmethod* most of the time)
and some proxy methods for its *queryMethods*. You can access all transformers in `Commons.DatabaseLayer` module.

### Database access
This section will introduce the database access wrappers at the lowest layer.
Database manipulation in the project is based on `SQLAlchemy` repository, and provides a more powerful pattern to manipulate
databases (source in `Scripts/databaseInit.py`). In general, the accession to a certain datatable requires a dataunit class derived from `Base` and a wrapper 
to data-manipulate methods provided by `SQLAlchemy`. A basic class `BasicManipulateMethods` is defined as the ancestor of
all data-manipulate wrappers which provides some interfaces with high usability (e.g. `SmartInsert`, `CheckExist`, etc).
As for every datatable, there should be a *XXXQueryMethods* class extending `BasicManipulateMethods`, in which one should
implement all the abstract methods demanded by the basic methods. For example, `RepresentationMethods` class is dedicated 
for accessing data in *pwrepresentation* datatable using `PwRepresentation` type as dataunit.
In addition, there may be some separate methods in `Scripts/databaseInit.py` providing certain single function like `parseLineToPIIUnit`
method. It's not recommended to use those methods because they would be deprecated in the future. Always consider using 
`BasicManipulateMethods` for high-level manipulations.  


### Build database
All database-building code is included in `Scripts/databaseInit.py`, which is the highest level methods for building databases.
Raw PII dataset should be accessed and processed by `PreProcessor`, the high-level script is in *Scripts/call_databaseInit.py*. Intermediate datatables used in algorithms should manipulate
by `DatabaseTransformer` and high-level scripts locate in *Scripts/buildDatabase.py*.

### Process dataset
`Preprocessor`

## Data Structures Explanation
### Foreground parsing and database building data structures
#### PIIDataTypes



## Database structure
### `pwrepresentation` datatable
1. `representation`: rep containing pwStr string section
2. `representationStructure`: only rep structure, no string section
3. `representationHash`: hash of `representation`
4. `hash`: hash of `pwStr` + `representation`

## PII type 
| Tag | Description                                      |
|-----|--------------------------------------------------|
| N1  | FullName                                         |
| N2  | Abbreviate of name                               |
| N3  | Family name                                      |
| N4  | Given name                                       |
| N5  | First character of given name append family name |
| N6  | First character of family name append given name |
| N7  | Family name capitalized                          |
| N8  | First character of family name                   |
| N9  | Abbr of given name                               |
| B1  | Birthday in YYYYMMDD                             |
| B2  | MMDDYYYY                                         |
| B3  | DDMMYYYY                                         |
| B4  | MMDD                                             |
| B5  | YYYY                                             |
| B6  | YYYYMM                                           |
| B7  | MMYYYY                                           |
| B8  | YYMMDD                                           |
| B9  | MMDDYY                                           |
| B10 | DDMMYY                                           |
| A1  | Account                                          |
| A2  | Letter segment of account                        |
| A3  | Digit segment of account                         |
| E1  | Email prefix                                     |
| E2  | Letter segment of email                          |
| E3  | Digit segment of email                           |
| E4  | Email site like qq, 163                          |
| P1  | Phone number                                     |
| P2  | First three digits of phone number               |
| P3  | Last four digits of phone number                 |
| I1  | Id card number                                   |
| I2  | First three digits of idCard                     |
| I3  | First six digits of idCard                       |



## Journal
## 10.27
1. *(TODO)* To support flexible-formatted datasets, treat the first line as field name, format in csv
2. *(TODO)* Complete develop documentation and requirements, add support for running from source code
3. Latest accuracy: 0.3278

### GUI optimize(8.29)
1. Progress bar, only-one running task
2. If a field is missing in PII data given, then all the patterns that need this field would be excluded
3. *(Solved)* TextBrowser.append is not thread-safe, define a worker to emit signal and connect to append-slot
4. Add content limitation to TextBrowser
5. Complete GUI optimize

### GUI and github doc(8.28)
1. Enable PIITagContainer to support empty fields 
2. Cannot patch dialog in QThread(even when use consumer thread to patch dialog)
3. Implement all main functions! Need tests
4. *(Solved)* Add multi-thread to PII data processing

### Optimize(8.26)
1. (5:5 train:test, 11w): model with 'gini': 452M, 0.3396; model with 'entropy': 451M, 0.3045
3. Add email site as a new tag type
4. Add FamilyName1st and GivenNameAbbr as new tag type
5. Optimize account lds tag for all segments
6. Accelerate the build procession with threadpool

### Accuracy assessment(8.25)
1. Add basic patterns into generated patterns(like "N1","B2")
2. *(TODO)* Figure out why basic patterns like "E1" and pws with high frequency like those started with "a" are not generated by the model. Optimize the train process and tune params 
3. First accuracy assessment result: in 12306 dataset with 11w PII data, using 0.7 for train-set and 0.3 for test, generating almost 3000 guesses, the proportion of successfully cracked is **0.3102**
4. *(TODO)* Compare the result against counterparts like **PassGAN**
5. 

### GUI and automating(8.24)
1. *(Solved)* Automate the datatable built, support to train by other datasets easily
2. *(Solved)* Regulate the result-testing procedure
3. *(Deprecated)* Build LDS datatable in (length, segmentStr)
4. *(Deprecated)* Generate guesses for PII-only(with LDS) patterns
5. Re-generate intermediate datatables in script

### (8.23)
1. The patterns generated exists some flaw, some character that have not ever occurred in the train data represent in classified results
That's led by the ambiguous conversion when counting serial number of characters. Therefore, `CharacterSecionFactory` and `CharacterLabel.toInt` should
be corrected to address this problem. The label integer of character section is calculated by `LabelParser.encodeCh` which is not ambiguous
2. *(Solved)* In generated patterns, the proportion of patterns starting with 'q' is abnormally large(570/1330) 
3. Solved problem[2] by adding an empty datagram with 6 begin sections for every pwStr and re-train the model
4. *(Solved)* Write GUI to generate guesses targeted on one PII data
5. *(TODO)* Test the accuracy of the model on other datasets
6. *(TODO)* Collect data breach of "Rootkit" or "ClixSense"

### Generate pattern and implement *GeneralPII* mode(8.20)
1. `test_generate_pattern` method: Implement pattern generating algorithm and generate most common used patterns to `patterns.txt`

- [x] Create data structures and corresponding factory
- [x] PII parsing phase: extend pii data structures and overwrite the PIIStructure parsing algorithm
- [x] Database build: create two new datatable `pwrepresentation_general` and `pwrepresentation_unique_general`
- [x] Overwrite representation select algorithm
- [x] Build training data: implement `GeneralPIIParser` to build feature list
- [x] Generate pattern: implement `GeneralPIIGenerator` to generate patterns

### Generator(8.19)
1. `PIIPatternGenerator`
2. *(Solved)* Get multiple classification results
3. *(Solved)* Generate a list of most common used password patterns
4. *(Solved)* Implement the hybrid mode, taking idle characters as `CharacterSection` rather than LDS segments
5. test_PIIGenerators.py: generate patterns
6. main_PII_Mode.py: train model

### Factory and train(8.18)
1. Add diagrams in `Diagrams` folder
2. Complete `PIIParser` and `PIIFactory` to build train dataset
3. Parser/PIIParsers.py: implement `PIISectionFactory` as the factory of `PIISection`
4. Adjust the defination of `PIISection` along with its fields. For now, PIISection's *type* field is the BaseType of section
like `PIIType.BaseTypes.Name`, *value* field denotes the specified pii type like `NameType.FullName`, and *value* field differs
for LDS section and PII section. In the condition of LDS section, *value* stores the length of LDS segment, as for PII section,
it stores a enum value of `PIIType` like `NameType.FullName`
5. `PIIParser` class has passed the initial test cases
6. *(Solved)* test `PIIParser` with various data items
7. Build train data and **training model** finished
8. *(Solved)* Implement classifier and generator


### Representation Resolver(8.16)
1. Convert all dataviews into datatable(I found queries on dataview behave too slow)
2. Resolver.`getInstance`(load all data in database) succeed in about 4s 
3. Resolver.`resolve` which is main algorithm succeed
4. Build datatable `pwrepresentation_unique` to store the unique representation and structure of every password string 
5. **Foreground Api hierarchy**: `Scripts/databaseInit.py`(bottom) => `Commons/DatabaseLayer.py`(Transformers) => `Scripts/Units`(flexible apis) => `Parser.PIIParsers`(top)
6. Test the unique datatable in `buildDatabase/test_read_unique` method
7. *(TODO)* Build LDS segment datatable with priority possibility
8. *(TODO)* Enrich document for data structures and all modules for database building


### Database build(8.15)
1. Adjust `PIIVector` and `Tag` to adapt to express *representationStructure*
2. Add *representationStructure* field in datatables
3. Complete representation extraction
4. Refactor all DatabaseTransformers with `Singleton`
5. Move all datastructures in `Parsers.PIIParser` to `Parser.PIIDataTypes`

### Database build(8.14)
1. Scripts/databaseInit.py: in `LoadDataset` method, add pii field format check before insert into datatable
2. Commons/BasicTypes.py: add `DefaultPII` 
3. Commons/Utils.py: `parsePIIUnitToPIIAndPwStr` add PII fields check and default value
4. Scripts/call_databaseInit.py: Build *pii* datatable using `test_load_dataset` method: there are duplicates in *pii* table, but it would not lead to any impact. **131653 items**
5. Scripts/buildDatabase.py: Build *pwrepresentation* datatable using `buildPwRepresentationTable` method: (**no duplicate**) **222937 items**
6. *(Solved)* Commons/DatabaseLayer.py.`getPwRepresentation`: Representation hash should exclude vector str(part of pwStr). 
Refactor the hash calculation process of database unit, and rebuild table `pwrepresentation` in *buildDatabase.py*
7. Access to test in *Tests/test_DatabaseLayer* in method `test_get_pw_representation`
8. *(TODO)* Illustrate the role and relationship of all data-structures, especially that of PII. 
9. *(Solved)* Overwrite the __copy__ method of `PIIRepresentation` to avoid mutate origin representation object when calculate
hash

### PII algorithms(8.13)
1. *(Solved)* Representation => DatagramList
2. *(Solved)* Build a table to store the final representation of password
3. Create `pwrepresentation` table to store passwords and corresponding representations
4. Create `representation_frequency` view to store frequency of representations
5. *(Solved)* Build `pwrepresentation` and `representation_frequency` tables with data
6. Scripts/databaseInit.py: refactor the query code with an ancestor class `BasicManipulateMethods`, have added Entity
type and QueryMethods for each table/view.


### Dataset preprocessor refactor(8.12)
1. Parser/BasicPreprocessor.py: refactor class `BasicPreprocessor`, add `FilePreprocessor` and `DatabasePreprocessor`
2. Parser/PIIPreprocessor.py: refactor class `PIIPreprocessor`
3. *(Solved)* test_PIIPreprocessor.py
4. *(TODO)* Implement full PII algorithms and join up the `PIIParser` to `PIIPreprocessor`

### Dataset processor(8.11)
1. Load 12306 dataset with 13w PII data and password into mysql database "dataset12306"
2. Parse fullName of PIIUnits and build the whole database
3. *(Solved)* Commons/Utils.py: Convert PIIUnit into standard PII model 

### RFGuess-PII foreground dataset handler and middle representation selector(8.7)
1. Commons.Utils.py: add class translation
2. *(Solved)* PIIParsers.py: recursive get all representation algorithm gets a wrong output


### RFGuess-PII foreground dataset handler(8.6)
1. PIIStructureParser: given pii and password string, output all vectors (LDS mode)
2. PIIParsers.py: *(TODO)* select a representation of pwStr, convert into Password, walk through and get Datagram list
3. *(TODO)* Refactor PasswordParser to fit the new design structure

### RFGuess-PII PIIParsers(8.5)
1. PIIFullTagParser: extract pii-tags with the given PII info
2. parseStrToPIIVector: extract all PII structure representations of password s, output PIIVector list which can directly feed RF model
3. LDS test and recursive algorithm test

### RFGuess-PII(8.4)
1. There is two choices in terms of password vector format, on the one hand, vectors only consist of type-based PII tag and character vector,
the other option is composed type-based tag and length-based tag with no specific character participating the training phase. As for the latter, 
the password "john@0728" would be parsed to "N4S1B4", at generating phase, "S1" will be addressed by selecting the top-10 most frequent fractions 
in the dataset, this way is certainly more conclusive about the rule of people constructing passwords but the generated result may be redundant.
The former method could need larger dataset on training a universal enough model but would perform more accuracy.
2. When generating guesses, deploy a transition layer to extend the selected rule, such as birthday date can be either parsed into "0607" and "67".


### RFGuess-PII(8.3)
1. Resolve password string into 26-dim vector composed of both CharacterVector and **PIIVector**
    - PIIVector: <PII Type(U,B,N...), PII Value(U1,B1...), 0, 0>
    - Determine the PII structure of every password with the **global frequency**
2. Notice both feature and label would have PII vectors, so does the generated guesses
3. Commonly train RF model, get the subsequent character(or PII tag) of the given prefix
4. Convert PII tag into PII string based on the real user information, get the final guess


### Dependency Injection(8.2)
- Core.Decorators.py: @Bean, @Autowire defination
- Core.Utils.py: Record the relationship of decorators and classes/functions 
- Core.__init__.py: Scan workspace find certain directories to import Components and Beans
- Context.Context.py: Container add objects to Context and ApplicationContext is defined to provide beans and components to user.
- Core.Caller.py: ComponentWrapper which denotes a task unit, can record Component status and multi-thread is on the fly; And ComponentContainer is to maintain all components, dispatch orders to wrappers
- Core.Application.py: ApplicationWrapper provide user interface
- Core.Config.py: *(TODO)* Define dependencies and inject user-defined Beans to Context

- *(TODO)* Beans can use Autowired to inject dependency
- *(TODO)* Training data generator, to feed the model in the period of training
- *(TODO)* Dictionary generator, to utilize trained models to circularly generate guesses
- 

### Data preproduce(7.31)

Regarding to the model which the paper above metioned, implement the transformation from primitive password string to
26-dimension vector which would feed Desicion Tree as feature vector, as well as the lable respectively.

### DT and RF model(8.1)

Implement DT and RF trainning and classification function whose usage can be found in *test.py*

### Inversion of Control(8.1)

#### ApplicationMain.py implemented by user(TODO)
1. In Config, Add dependency: e.g add a sampleGenerator. Register **Beans**(Beans are independent) to Container
2. Scan Beans package: add beans into Container
3. Apply for subjects like DTTrainner that depend on at least one Bean, and add as dependency into Container. If there is no certain Bean required in Container, throw Exceptions
4. Implement custom Component, use Autowired annotation to inject dependency
5. Application run: inject dependencies to Components. And run Components implemented by user.

#### Problems
1. Core.Utils.py: how to get the class object by moduleName and className



### TODO

For intra-
site scenarios, we randomly select 0.01M, 0.1M, and 1M
(M=million) passwords from Rockyou as the training set, re-
spectively, and randomly select 100,000 passwords from the
remaining dataset as the test set.

smooth character

