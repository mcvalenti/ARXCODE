# -*- coding: utf-8 -*-
"""
Created on Mon Jan 11 11:18:32 2016

Track del encuentro ENVI-COSMOS

@author: mcvalenti
"""

from gmtpy import GMT

gmt = GMT( config={'BASEMAP_TYPE':'fancy'})

gmt.pscoast( R='g',
             J='G70/-51/6i',
             B='15g15',              # grid
             N='1',
             S=(173,216,230),      # wet fill color 
             G=(144,238,144),      # dry fill color
             W='thinnest' )        # shoreline pen
             

gmt.psxy( '../alfdelenvi.txt',
          R='',
          J='',
          O='-',
          S='t0.05',
          K='K')
          
gmt.psxy( '../alfadelcosmos.txt',
          R='',
          J='',
          O='',
          S='t0.05',
          K='K')


gmt.save('../trackencuentro.ps')