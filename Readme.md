<div align='center'>

<h1>RFGuess(Random Forest Password Guessing model)</h1>



</div>

## Overview
This repository contains a reproduction for [Password Guessing Using Random Forest](https://www.usenix.org/conference/usenixsecurity23/presentation/wang-ding-password-guessing) paper in which author raised a series of new methods to translate PII data(Personal Identifiable Information) into structures that perform pretty well in classical machine learning models.
I have implemented the key concept of the paper and programmed a easy-to-use tool for training models, generating patterns, conducting guesses and assessing accuracy. This repo contributes:
- A GUI program exclusive for PII-based targeted password guessing scenario
- A pretrained model



## Features
- **Targeted password guessing based on PII**(crack the password of a given user)
- A pre-trained model(get [here](https://github.com/PadishahIII/RFGuess/releases/download/executable/model.clf)) ready to use which is trained on a dataset with 11w data
- Generate password patterns based on PII dataset
- Conduct password guesses for given personal information
- Support to train specified model for self-defined datasets
- Support to assess the accuracy of generated guesses


[//]: # (## Getting Started)

## Prerequisites

- Python3
- Mysql 8.0.32
- Sklearn<a href="https://scikit-learn.org/stable/install.html"> Here</a>
- PyQt5<a href="https://pypi.org/project/PyQt5/"> Here</a>


## Usage

Run the executable file and you will see the panel as below:
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/f255451d-9247-4c9c-ae44-575b912e6fb1)


There are three main modules in the user interface: guess-generator, pattern-generator and model-trainner. 

### Generate pattern(pattern-generator)
First you should get a trained model(whether train by yourself in [model-trainner](#train-your-own-model) or use the pretrained model at [rfguess.clf](https://github.com/PadishahIII/RFGuess/releases/download/executable/model.clf)).
Then you could set a limitation on the number of pattern to generated and start generating.

1. Load model(.clf)
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/34a03037-64b5-43fe-90e0-8d359828575b)


2. Assign output path and set limit
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/c228481a-09f3-4127-b4c0-ba1eff076c29)



### Generate password dictionary(guess-generator)
This module requires a pattern file(see [Appendix](#appendix) for more detail) and PII data of the target user. You can load the pattern file generated by pattern-generator or use the [default pattern file](https://github.com/PadishahIII/RFGuess/releases/download/executable/patterns.txt).

1. Load pattern file
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/e3efb8a3-053a-4403-bca5-555a5b62f388)


2. Fill in PII data
You should input the personal data of the target user or load data from json file([format](https://github.com/PadishahIII/RFGuess/blob/executable/pii.json))
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/4ce60737-9e2c-40ef-abb0-922c70bb6fa8)

![image](https://github.com/PadishahIII/RFGuess/assets/83501709/23ea89e6-2af5-4738-8f45-cf94015b2883)


3. Generate password dictionary
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/caa52831-d2ec-4e54-97ac-2237bac19c51)



### Train your own model
The model training procession of Machine Learning is pretty more hassle than that of Deep Learning. Algorithms in this program need to use mysql database to store intermediate data structures while processing original dataset. Fortunately, you only need to have a mysql server normally running and just provide a database Url to connect. All the data structures will be configured automatically.


1. Connect to your database and import database structure
Connect to database URL:
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/d412fadc-2b48-4750-b761-42c5a54b3288)

Import sql file(get [here](https://github.com/PadishahIII/RFGuess/blob/executable/database_structure.sql)):
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/7cfdbd98-4a3e-4513-80f8-8e76cbf2677e)

2. Load your pii dataset(.txt)
The pii dataset should in the below format:
  - every line contains one pii data
  - every line should have several fields and in format of
      ```
    <email>---<account>---<name>---<idCard>---<password>---<phoneNumber>
      ```
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/3a81945e-a2ec-42ff-b1b7-3a01deb9527d)


4. Analyze and process dataset
This step will analyze the pii dataset to some intermediate datatables.
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/c73d864d-55d6-43f0-bceb-204978e3bb07)


6. Train model
You will train a classifier model and dump into a .clf file.
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/06925559-485f-4908-802a-746311ac1f55)


7. Assess accuracy
To assess accuracy of your already trained model, this step will use 50% of your dataset as train-set and other 50% as test-set, generate a password dictionary for every pii data and check whether the correct password falls in the dictionary.
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/7f634c62-bfc9-438f-b2e8-57fd8272062c)


8. Restore the status of last run
With "Update Status" button, you can load the progress of last run and check status of each phase.
![image](https://github.com/PadishahIII/RFGuess/assets/83501709/eca7e301-30a6-4866-9b82-ef8d2227f70e)



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


