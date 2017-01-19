'''
Created on 19/01/2017

@author: mcvalenti
'''
import calendar


def toTimestamp(d):
    return calendar.timegm(d.timetuple())