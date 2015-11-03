
Twitter_DA_Recognition
Hasso-Plattner-Institut. Master Thesis. Automatic dialog act recognition in Twitter conversation.

Before starting the applications create in postgres a Database with the name : "dialogue_acts", the owner is postgres. 
Create a database in MongoDb with the name "DARecognition"
Put goldStandard.xlxs to the DATA folder.
Create a folder in DATA with the name "annotationed" and unzip webanno-projectexport.zip

To start the application run main.py file
By defaul the gold standard will be inserted to the dialogue_acts daabase and you will be asked to choose spervised learning algorithm, 
with what feature set the chosen algorithm(s) should be trained with. How many words do you want to add to the feature set? 
And how the evaluation should look like (either you can observe evaluation for each DA with different measures, 
as well as confusion matrix, or only evaluation of the methods and feature sets, without detailed inforamation about each DA).

If you want to start analyzing the origianl data (merging as well) comment in/out in main.py  the line: analyze_original_data(connection, cursor)
Merged data will apper in DATA/goldenStandard/.

Requerments

Python 2.7.9
MongoDB 3.0
PostgreSQL 9.3

Libraries for python

pymongo 3.0.3
psycopg2 1.1.21


langid 1.1.5

pycrfsuite
hmmlearn 0.0.1
pattern.de 2.6
sklearn
treelib 1.3.2
nltk 3.1
numpy 1.10.1

xlrd 0.9.4
xlsxwriter 0.7.7
csv 1.0




