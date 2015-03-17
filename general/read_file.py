__author__ = 'snownettle'
import os.path


def readTXT(file_name):
    if os.path.exists(file_name) is True:
        with open(file_name) as f:
            content = f.read()
            return content
    else:
        print 'There is no such file'
        return None


