__author__ = 'snownettle'
import glob
import os
from mongoDB import  importTwitterConversation


def import_raw_twitter_data(directory_path, collectionRawTwitterData):
    for filename in glob.iglob(os.path.join(directory_path,'*.txt')):
            content = readTXT(filename)
            print filename + ' will be added to DB'
            importTwitterConversation.importData(collectionRawTwitterData, content)
            print filename + ' is added to DB'


def readTXT(fileName):
    with open(fileName) as f:
        content = f.read()
        return content
