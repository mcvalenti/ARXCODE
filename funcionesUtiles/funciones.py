'''
Created on 19/01/2017

@author: mcvalenti
'''
import os
import calendar


def toTimestamp(d):
    return calendar.timegm(d.timetuple())

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)