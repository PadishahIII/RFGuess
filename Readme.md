# Random Forest Password Guessing Model

## Overview

https://www.usenix.org/conference/usenixsecurity23/presentation/wang-ding-password-guessing

## Model Parameter
1. min_samples_leaf=10: given the length of passwords almost larger than 6, a password would generate 9~10 datagrams averagely, so the minimum datagram number of a leaf is set to 10
2. n_estimators=30: 30 decision trees
3. criterion='gini': CART decision tree

## Journal

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

