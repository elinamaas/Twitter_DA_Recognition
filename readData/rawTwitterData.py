__author__ = 'snownettle'
import glob
import os
from mongoDB import importData
from general import read_file


def import_raw_twitter_data(directory_path, collection):
    for filename in glob.iglob(os.path.join(directory_path,'*.txt')):
            content = read_file.readTXT(filename)
            print filename + ' will be added to DB'
            importData.import_from_file(collection, content)
            print filename + ' is added to DB'

