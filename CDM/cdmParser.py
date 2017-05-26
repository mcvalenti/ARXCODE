'''
Created on 26/05/2017

@author: mcvalenti
'''
#from xml import etree
import xml.etree.ElementTree
#e = xml.etree.ElementTree.parse('cdmTest.xml').getroot()

root = xml.etree.ElementTree("root")
print root.tag
# root.append( etree.ElementTree("child1") )
# root.append( etree.ElementTree("child2") )
# root.append( etree.ElementTree("child3") )
# print(etree.tostring(root, pretty_print=True))