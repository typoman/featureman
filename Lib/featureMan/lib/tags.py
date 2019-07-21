import os

currentDir = os.path.dirname(os.path.realpath(__file__))

def txt2dic1(mfile):
    # Function that takes a tab seperated file and produces a dictionary
    # It also igonres the lines that starts with # character
    
    File = open(mfile , 'r')
    List = File.read().split('\n')
    Tags = {}
    for line in List:
        if line and line[0] != '#':
            splittedLine = []
            splittedLine = line.split('\t')
            Tags[splittedLine[0]] = splittedLine[1]
    File.close()
    return Tags

def txt2dic2(mfile):
    # Function that takes a tab seperated file and produces a dictionary
    # It also igonres the lines that starts with # character
    
    File = open(mfile , 'r')
    List = File.read().split('\n')
    Tags = {}
    for line in List:
        if line and line[0] != '#':
            splittedLine = []
            splittedLine = line.split('\t')
            Tags[splittedLine[0].lower()] = splittedLine[1]
    File.close()
    return Tags


scriptTags = txt2dic1(currentDir+'/scriptTags') # query Script Name and get the open type tag
languageTags = txt2dic2(currentDir+'/languageTags') # query Language Name and get the open type tag

