# Random Forest Password Guessing Model

## Overview

https://www.usenix.org/conference/usenixsecurity23/presentation/wang-ding-password-guessing

## Model Parameter
1. min_samples_leaf=10: given the length of passwords almost larger than 6, a password would generate 9~10 datagrams averagely, so the minimum datagram number of a leaf is set to 10
2. n_estimators=30: 30 decision trees
3. criterion='gini': CART decision tree

## Journal

### RFGuess-PII foreground dataset handler(8.6)
1. PIIStructureParser: given pii and password string, output all vectors (LDS mode)
2. 

### RFGuess-PII PIIParsers(8.5)
1. PIIFullTagParser: extract pii-tags with the given PII info
2. parseStrToPIIVector: extract all PII structure representations of password s, output PIIVector list which can directly feed RF model
3. *(TODO)*: LDS test and recursive algorithm test

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

