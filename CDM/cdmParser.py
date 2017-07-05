'''
Created on 26/05/2017

Parseo del CDM en formato XML.

@author: mcvalenti
'''
import xml.etree.ElementTree as ET

class CDM():
    def __init__(self,archivo):
        self.tree=ET.parse('../CDM/archivos/'+archivo)
        root = self.tree.getroot() 
        self.TCA=None
        self.MISS_DISTANCE=None
        self.POC=None
        self.mision_name=None
        self.noradID_mision=None
        self.deb_name=None
        self.noradID_deb=None
        
        for bod in root.iter('body'):
            self.TCA=bod[0][1].text
            self.MISS_DISTANCE=bod[0][2].text
            self.POC=bod[0][14].text
            
        n=0    
        for meta in root.iter('metadata'):
            if n == 0:
                self.mision_name=meta[1].text
                self.noradID_mision=meta[2].text
            else:
                self.deb_name=meta[1].text
                self.noradID_deb=meta[2].text
            n=n+1
      
        
        
def extraeCDM(archivo):
    """
    Extrae los datos de un CDM en formato XML.
    inputs
        archivos: nombre de archivo CDM en formato .xml (string)
    Outputs
        TCA: tiempo de maximos acercamiento. (string)
        Obj1, Obj2: nombre de objetos implicados (string)
        miss_dist: minima distancia (string)
        poc: probabilidad de colision (string)
    """
    tree = ET.parse('../CDM/archivos/'+archivo)
    root = tree.getroot()

    obj_m=[]
    obj_d=[]

    """
    ENCUENTRO
    """
#     tca_mio=cdm.find('body/relativeMetaData')
#     print tca_mio.attrib
    for bod in root.iter('body'):
        TCA=bod[0][1].text
        MISS_DISTANCE=bod[0][2].text
        POC=bod[0][14].text
        
    n=0    
    for meta in root.iter('metadata'):
        if n == 0:
            obj_m.append(meta[1].text)
            obj_m.append(meta[2].text)
        else:
            obj_d.append(meta[1].text)
            obj_d.append(meta[2].text)
        n=n+1

    obj_list=[obj_m,obj_d]    
    return TCA,MISS_DISTANCE,POC,obj_list
    
    
if __name__=='__main__':
    
    archivo='cdmTest.xml'
    TCA,MISS_DISTANCE,POC,obj_list= extraeCDM(archivo)
    """
    Impresion por pantalla.
    """
    info1='Acercamiento entre '+str(obj_list[0][0])+' y '+str(obj_list[1][0])
    print '=============================================================='
    print info1
    print '=============================================================='
    print 'Mision Id= ', str(obj_list[0][1])
    print 'Target Id= ', str(obj_list[1][1])
    print 'Tiempo de maximo acercamiento= ', TCA
    print 'Minima Distancia = ', MISS_DISTANCE
    print 'Probabilidad de Colision = ', POC
    
    
#         """
#         Pruebas ENVISAT-COSMOS
#         """
#         self.TCA=datetime(2008,1,9,19,0,30,6)
#         TCAstr0=datetime.strftime(self.TCA,'%Y-%m-%dT%H:%M:%S')
#         self.sat_idc='27386' #ENVISAT
#         self.deb_idc='12442' #COSMOS
#         
#         Cd=np.array([[4.1345498441906514,-0.031437388833697122,0.078011634263035007],
#                 [-0.031437388833697122,0.0025693554190851101,-0.014250096142904997],
#                 [0.078011634263035007,-0.014250096142904997,0.096786625771746529]])
#     
#         Cm=np.array([[4.8247926515782202,0.05994752830943241,0.049526867540809635],
#                 [0.05994752830943241,0.019150349628774828,0.012470649611436152],
#                 [0.049526867540809635,0.012470649611436152,0.012649606483621921]])