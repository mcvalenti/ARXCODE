import glob
import csv
from datetime import datetime
from operator import itemgetter
import collections
from collections import OrderedDict
from CDM import CDM

"""
* a partir del msg_id y tca
* ordeno los cdm por tca
"""

MSG = collections.namedtuple('MSG', ['msg_id','O1_ID','O2_ID','msg_epoch','TCA','miss_distance','collision_probabiliy']) # 'O1_ID','O2_ID','TCA','miss_distance'])
CDMs = []

# extract data from file
msg_id=[]
O1_id=[]
O2_id=[]
tca=[]
miss_distance=[]
relative_position_r=[]
relative_position_t=[]
relative_position_n=[]
# Looks for the CDMs already in CDM folder
path_files=glob.glob('test_CDM/CDM1.txt')
print path_files
for pf in path_files:
    print pf
    myCDM = CDM(pf)
    CDMs.append(MSG(myCDM.MESSAGE_ID,myCDM.O1_OBJECT_DESIGNATOR,myCDM.O2_OBJECT_DESIGNATOR,myCDM.CREATION_DATE,myCDM.TCA,myCDM.MISS_DISTANCE,myCDM.COLLISION_PROBABILITY)) #myCDM.O1_OBJECT_DESIGNATOR,myCDM.O2_OBJECT_DESIGNATOR,myCDM.TCA,myCDM.MISS_DISTANCE))

with open('cdms_asi.csv', 'w') as f:
    w = csv.writer(f)
    w.writerow(('MSG ID','O1_ID','O2_ID','MSG EPOCH', 'TCA','Miss Distance','PoC'))    # field header
    w.writerows([(msg, obj1_id, obj2_id,msg_epoch, tca,miss_distance,poc) for msg, obj1_id, obj2_id,msg_epoch, tca, miss_distance,poc in CDMs])


# # #csv Example si hay dos elementos, msg_id y tca
# # sort list by age
# sort_CDM=OrderedDict(sorted(CDMs, key=itemgetter(MSG._fields.index('TCA'))))
# print sort_CDM
# # 
# with open('output.csv', 'w') as f:
#     w = csv.writer(f)
# #for s in sort_CDM:
#     w.writerow(('Msg_id', 'tca'))    # field header
#     w.writerows([(name, data) for name, data in sort_CDM.items()])
