# Random Forest Password Guessing Model

## Overview

https://www.usenix.org/conference/usenixsecurity23/presentation/wang-ding-password-guessing

## Model Parameter
1. min_samples_leaf=10: given the length of passwords almost larger than 6, a password would generate 9~10 datagrams averagely, so the minimum datagram number of a leaf is set to 10
2. n_estimators=30: 30 decision trees
3. criterion='gini': CART decision tree

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
Raw PII dataset should be accessed and processed by `PreProcessor`. Intermediate datatables used in algorithms should manipulated
by `DatabaseTransformer`.

### Process dataset
`Preprocessor`


## Journal
### Database build(8.14)
1. Scripts/databaseInit.py: in `LoadDataset` method, add pii field format check before insert into datatable



### PII algorithms(8.13)
1. *(TODO)* Representation => DatagramList
2. *(TODO)* Build a table to store the final representation of password
3. Create `pwrepresentation` table to store passwords and corresponding representations
4. Create `representation_frequency_view` view to store frequency of representations
5. *(TODO)* Build `pwrepresentation` and `representation_frequency_view` tables with data
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

