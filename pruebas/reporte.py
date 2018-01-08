'''
Created on 8 ene. 2018

El siguiente modulo es una prueba para la generacion
de reportes en formato pdf

@author: curso
'''

from reportlab.pdfgen import canvas
from datetime import datetime

# ------------------------------------------------------------
# DATOS
# ------------------------------------------------------------
d = datetime.utcnow()
d_str= d.strftime("%Y-%m-%d %H:%M:%S")
rep_name= "CRA_NSAT_NDEB_TCA_GDATE"
rep_id="35601"
op = "Valenti Cecilia"
mission= "SAC-D"

# ------------------------------------------------------------
# IMPRESION DE DATOS 
# ------------------------------------------------------------
canvas = canvas.Canvas("../Encuentro/registros/hello.pdf")

canvas.setLineWidth(.3)
canvas.setFont('Helvetica', 12)

# Consignas 
canvas.drawString(30,750,'COLLISION ASSESSMENT REPORT (CRA)')
canvas.drawString(30,720,'REPORT NAME:')
canvas.drawString(370,720,'REPORT ID:')
canvas.drawString(30,705,'REPORT DATE:')
canvas.drawString(30,690,'OPERATOR:')
canvas.drawString(30,675,'MISSION:')
canvas.drawString(30,650,'Situacion:')
canvas.line(30,646,450,646)
canvas.drawString(30,635,'SATELLITE ID:')
canvas.drawString(30,620,'DEBRIS ID:')
canvas.drawString(30,605,'TCA:')
canvas.drawString(30,590,'INPUTS (manual/CDM):')
canvas.drawString(30,560,'Configuracion:')
canvas.line(30,556,450,556)
canvas.drawString(30,535,'PoC method:')
canvas.drawString(30,520,'Hitradius:')
canvas.drawString(30,495,'RESULTADOS:')
canvas.line(30,491,450,491)
canvas.drawString(30,470,'TCA:')
canvas.drawString(30,455,'Miss Distance:')
canvas.drawString(30,440,'PoC:')

# Informacion
canvas.drawString(150,720,rep_name)
canvas.drawString(460,720,rep_id)
canvas.drawString(150,705,d_str)
canvas.drawString(150,690,op)
canvas.drawString(150,675,mission)

canvas.save()
