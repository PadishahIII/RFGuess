<div align='center'>

<h1>RFGuess(Random Forest Password Guessing model)</h1>



</div>

## Overview
This repository contains the reproduction for the paper [Password Guessing Using Random Forest](https://www.usenix.org/conference/usenixsecurity23/presentation/wang-ding-password-guessing). The author proposes a set of new methods to translate PII(Personal Identifiable Information) data into structures that perform quite well in classical machine learning models.
I have implemented the main concept of the paper and programmed an easy-to-use tool for training models, generating patterns, conducting guesses and evaluating accuracy. This repo contributes:
- A GUI program exclusively for the PII-based targeted password guessing scenario
- A pre-trained model



## Features
- **PII-based targeted password guessing**
- A pre-trained model(get [here](https://github.com/PadishahIII/RFGuess/releases/download/executable/model.clf)) ready to use which is trained on a dataset with 11w data
- Generate password patterns based on PII dataset
- Conduct password guesses for given personal information
- Support for training specified model for self-defined datasets
- Support for evaluating the accuracy of generated guesses


[//]: # (## Getting Started)

## Prerequisites

- Python3
- Mysql 8.0.32
- Sklearn<a href="https://scikit-learn.org/stable/install.html"> Here</a>
- PyQt5<a href="https://pypi.org/project/PyQt5/"> Here</a>


## Usage

- [Main window](#main-window)

- [Generate pattern](#generate-patternpattern-generator)

- [Generate password dictionary](#generate-password-dictionaryguess-generator)

- [Train your own model](#train-your-own-model)

---

### Main window

Run the executable file and you will see the panel as below:
![1](https://github.com/PadishahIII/RFGuess/assets/83501709/18c4a5e8-8e6c-4593-9c75-3c3f1b634969)




There are three main modules in the user interface: Guess-Generator, Pattern-Generator and Model-Trainner. 

### Generate pattern(Pattern-Generator)
First you should get a trained model(whether you train by yourself in [model-trainner](#train-your-own-model) or use the pre-trained model from [rfguess.clf](https://github.com/PadishahIII/RFGuess/releases/download/executable/model.clf)).
Then set a limit on the number of patterns to be generated and start generating.

1. Load model(.clf)
![2](https://github.com/PadishahIII/RFGuess/assets/83501709/d6fcc6b2-dc39-43fc-8009-9521d8f96deb)



2. Assign output path and limit
![3](https://github.com/PadishahIII/RFGuess/assets/83501709/a3476070-35fa-4c82-a0ab-a660b0722875)




### Generate password dictionary(Guess-Generator)
This module requires a pattern file(see [Appendix](#appendix) for more detail) and PII data of the target user. You can load the pattern file generated by Pattern-Generator or use the [default pattern file](https://github.com/PadishahIII/RFGuess/releases/download/executable/patterns.txt).

1. Load pattern file
![4](https://github.com/PadishahIII/RFGuess/assets/83501709/522a0885-b47c-4373-ab83-6ec479cfcf6c)



2. Fill in PII data
Input the personal data of the target user or load data from json file([format](https://github.com/PadishahIII/RFGuess/blob/executable/pii.json))
![5](https://github.com/PadishahIII/RFGuess/assets/83501709/b0e7a1ad-37fc-49f5-95d9-d50be3a5996d)


![6](https://github.com/PadishahIII/RFGuess/assets/83501709/2eab05b2-0d1e-4740-bcb0-f41efee33f4d)



3. Generate password dictionary
![7](https://github.com/PadishahIII/RFGuess/assets/83501709/4f1c2279-c9df-41e8-8938-bb9a542a0ac8)




### Train your own model
The model training process of Machine-Learning is pretty more laborious than that of Deep-Learning. The algorithms in this program need to use mysql database to store intermediate data structures while processing the original dataset. Fortunately, you just need to have a normal running mysql server and just provide a database url to connect to. All the data structures are configured automatically.


1. Connect to your database and import database structure
   
Connect to database URL:
![8](https://github.com/PadishahIII/RFGuess/assets/83501709/c0f3055e-c5d0-4613-8be8-ddee2b1df729)


Import sql file(get [here](https://github.com/PadishahIII/RFGuess/blob/executable/database_structure.sql)):
![9](https://github.com/PadishahIII/RFGuess/assets/83501709/4f4e7a6e-9a6c-49e3-9806-d73c2ac34e8d)


2. Load your PII dataset(.txt)
   
The PII dataset should in csv format and comply with the principles below:
  - the first line presents field names
     - field name should fall into ['account', 'name', 'phone', 'idcard', 'email', 'password'], **case-insensitive**
     - you can include any combination of the allowed fields but ***name*** and ***password*** are mandatory
  - each line contains one PII data
  - each line should have several fields and separated by comma
  - blank characters will be ignored


A legal dataset is presented like:
```
name, email, password, phone
张三, 350777@aa.com , zhangsan, 111122222
John, 3333@bb.com, 3333, 44444
Jason Harris, aaaa@aa.com, 5555, 5555
```

You can specify the character set of the target dataset by *Charset* edit box.
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/4cdf1c79-6b55-4ec0-9132-af9473c2d7ab)

Push *Load PII Data* button and wait. Your dataset will be consumed and stored in database after some procession.
![10](https://github.com/PadishahIII/RFGuess/assets/83501709/4fb33e8c-999c-4bc9-9bba-d1b9e3c31d61)



4. Analyze and process dataset
   
This step will analyze the PII dataset to some intermediate data.
![11](https://github.com/PadishahIII/RFGuess/assets/83501709/03f1141e-b59d-41fd-b2f7-23d7a772f9a7)



6. Train model
   
You will train a classifier model and dump into a .clf file.
![12](https://github.com/PadishahIII/RFGuess/assets/83501709/a9aff7ca-274a-4c32-9900-e8cb9bb25110)



8. Evaluate accuracy
   
To evaluate the accuracy of a model, this step uses 50% of your dataset as train-set and other 50% as test-set, generates a password dictionary for each PII data and checks whether the correct password falls into the dictionary.
![13](https://github.com/PadishahIII/RFGuess/assets/83501709/6fda460b-1ab6-4284-b7cf-4d4a07a94c75)



9. Restore the status of last run
Use "Update Status" button to load the progress of the last run and check the status of each phase.
![14](https://github.com/PadishahIII/RFGuess/assets/83501709/e85b101c-75b0-40e2-8bd5-8a9ec0fa5768)


## Advanced Configuration
See more detailed configuration at [Config.py](https://github.com/PadishahIII/RFGuess/blob/master/Parser/Config.py).

**Algorithm configuration**
*Markov n-gram* model is used in the main algorithm, you can set *n* by *pii_order* parameter:
```python
pii_order = 6 
```

You can control the limit of guesses by the two following thresholds, which are calculated according to the possibility of the growing pattern. 
A pattern is adopted only if its possibility is greater than the threshold. So the larger is the threshold, the lesser is the number of guesses, vice verse. It is notable that you should not set the threshold excessively small(lesser than *1e-11*) to avoid overwhelming by useless patterns. 

```python
general_generator_threshold = 1.2e-8
```

**Database configuration**
You can config the table names of database as you like:
```python
class TableNames:
    PII = "PII"
    pwrepresentation = "pwrepresentation"
    representation_frequency = "representation_frequency"
    pwrepresentation_frequency = "pwrepresentation_frequency"
    pwrepresentation_unique = "pwrepresentation_unique"
    pwrepresentation_general = f"{pwrepresentation}_general"
    representation_frequency_base_general = f"representation_frequency_base_general"
    representation_frequency_general = f"{representation_frequency}_general"
    pwrepresentation_frequency_general = f"{pwrepresentation_frequency}_general"
    pwrepresentation_unique_general = f"{pwrepresentation_unique}_general"
```

**Classifier configuration**

Tune the parameters of random forest by the following config:
```python
class RFParams:
    n_estimators = 30
    criterion = 'gini'
    min_samples_leaf = 10
    max_features = 0.8
```

---

## Build from source
This project is written by **Python3.11**. You can install dependencies by using pip:
```
pip install -r requirements.txt
```

And run the following command to launch the main window:
```
py main.py
```



## License

This code is released under an [MIT License](https://github.com/PadishahIII/RFGuess/blob/master/LICENSE). You are free to use, modify, distribute, or sell it under those terms.


## Contact

- 350717997@qq.com
  

Project Link: [https://github.com/PadishahIII/RFGuess](https://github.com/PadishahIII/RFGuess)

## Acknowledgements

- [Password Guessing using Random Forest](https://www.usenix.org/conference/usenixsecurity23/presentation/wang-ding-password-guessing)

# Appendix
## Pattern format
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


