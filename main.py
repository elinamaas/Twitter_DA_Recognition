
import glob
import os

for filename in glob.iglob(os.path.join('../../DATA', '*', '*.txt')):
    content = readTXT(filename)
    importTwitterConversation.importData('test2', content)
