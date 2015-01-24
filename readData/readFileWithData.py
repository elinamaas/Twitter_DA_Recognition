def readTXT(fileName):
    with open(fileName) as f:
        content = f.read()
        return content
