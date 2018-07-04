#!/usr/bin/python
import re
from datetime import datetime

class CDM():
    def __init__(self, filename):
        prepend = ''
        self.COMMENT = []
        self.O1_COMMENT = []
        self.O2_COMMENT = []
        with open(filename, "r") as fin:

            # loop to process all the lines 
            for line in fin:

                # remove non ascci chars
                line = re.sub(r'[^\x00-\x7f]',r'', line)

                # the COMMENT string are not parsed
                m = re.match('(COMMENT)\s*(\S.*)', line)
                if m:
                    name  = m.group(1)
                    value = m.group(2)
                # Parsing of string of type: name = value [dimension]
                # --- URL string are not parsed ---
                else:          
                    m = re.match('([A-Z\_]*)\ *\=([a-zA-Z0-9\,\.\-\:\ \_]*)(\[\S*\])?', line)
                    if m:
                        name  = m.group(1)
                        value = m.group(2)

                # The parameters have a name with O1 or O2 prepended (OBJECT1 OBJECT2)
                if name == 'OBJECT' and prepend == '':
                    prepend = 'O1_'
                elif name == 'OBJECT' and prepend != '':
                    prepend = 'O2_'

                # in case of COMMENT the remaining string is appended in a list
                if name == 'COMMENT':
                    name = prepend+name
                    exec('self.'+name+'.append(value)')
                else:
                    name = prepend+name
                    # string representing a number
                    v = self.isanumber(value)
                    if v != None:
                        exec('self.'+name+' = v')
                    # string representing a datetime
                    else:
                        v = self.isadatetime(value)
                        if v != None:
                            exec('self.'+name+' = v')
                        # only string
                        else:
                            exec('self.'+name+' = "'+value+'"')

    # return a float if the string represent a number
    def isanumber(self, a):
        try:
           val=float(a)
        except:
           val = None
        return val
    
    # return a datetime object if the string represent a "datetime"
    def isadatetime(self, s):
        try:
           val=datetime.strptime(s, '%Y-%m-%dT%H:%M:%S')
        except:
            try:
                val=datetime.strptime(s, '%Y-%m-%dT%H:%M:%S.%f')
            except:
                val = None
        return val   
    
# CDM class Test 
if __name__ == "__main__":

#    # define a CDM class
    myCDM = CDM('test_CDM/CDM1.txt')
    
#    # print all class members
    import inspect
    members = inspect.getmembers(myCDM)
    for member in members:
        print member[0]+': ', member[1]

#    # print some specific class member    
    print '------------------------'
    print 'MESSAGE_FOR', myCDM.MESSAGE_FOR
    print 'MESSAGE_ID', myCDM.MESSAGE_ID
    print 'MISS_DISTANCE',  myCDM.MISS_DISTANCE
    
    print 'O1_OBJECT_NAME: ', myCDM.O1_OBJECT_NAME
    print 'O2_OBJECT_NAME: ', myCDM.O2_OBJECT_NAME
    
    
    
    
    
