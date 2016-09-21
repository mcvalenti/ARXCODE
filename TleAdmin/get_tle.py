"""
Created on Tue Jul 12 14:21:56 2016

@author: curso
"""

from requests import session

class importar_tle():
    
    def __init__(self, cat_id,tca):
        f=open(cat_id+'.txt','w')
        data = {'identity': 'macecilia' , 'password': 'MaCeciliaSpace17'}
        noradId=cat_id
        y=tca.year
        m=tca.month
        di=tca.day
        df=di+2
        fecha=str(y)+'-'+'0'+str(m)+'-'+'0'+str(di)
        fecha1=str(y)+'-'+'0'+str(m)+'-'+str(df)
#       
        s=session()
        s.post('https://www.space-track.org/auth/login',data)
        fquery1 = "https://www.space-track.org/basicspacedata/query/class/tle/EPOCH/"+fecha+"--"+fecha1+"/NORAD_CAT_ID/" + str(noradId) + "/orderby/TLE_LINE1 ASC/format/tle"
        r = s.get(fquery1)
        f.write(r.text)
        print 'Se ha generado el archivo= ', cat_id,'.txt'



