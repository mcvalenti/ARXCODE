"""
Created on Mon Jan 11 11:18:32 2016

Track del encuentro ENVI-COSMOS

@author: mcvalenti
"""

from gmtpy import GMT

gmt = GMT( config={'BASEMAP_TYPE':'fancy'})

gmt.pscoast( R='0/280/-75/75', #g
             J='M6i', #'G70/-51/5i'
             B='15g15',              # grid
             N='1',
             S=(173,216,230),      # wet fill color 
             G=(144,238,144),      # dry fill color
             W='thinnest' )        # shoreline pen
           
gmt.psxy( '../Encuentro/archivos/15482U',
          R='',
          J='',
          O='-',
          S='t0.05',
          K='K')
           
gmt.psxy( '../Encuentro/archivos/27386U',
          R='',
          J='',
          O='',
          S='t0.05',
          K='K')


gmt.save('../visual/archivos/track.ps')

print 'Fin del procesamiento'
