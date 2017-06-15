from sgp4.earth_gravity import wgs72
from sgp4.io import twoline2rv
from datetime import datetime
from SistReferencia.sist_deCoordenadas import teme2tod, vncSis

f = open('tlesacd.txt','r')
g = open('cods05jun2013.txt','r')
cods = g.readlines()
#cuenta = 0
line1 = f.readline()
line2 = f.readline()
satellite = twoline2rv(line1, line2, wgs72)
t0 = satellite.epoch
dif = ()
poscods = ()
velcods = ()
#print type(t0)
print "Epoch: " ,t0
#	print satellite.epoch
for hora in range(0,24):
	for minuto in range(0,60):
		for segundo in range(0,60):
			datos = cods[segundo + minuto * 60 + hora * 3600].split()
			xcods = float(datos[2])
			ycods = float(datos[3])
			zcods = float(datos[4])
			xpcods = float(datos[5])
			ypcods = float(datos[6])
			zpcods = float(datos[7])
#			zosition, velocity = satellite.propagate(t0.year, t0.month, t0.day, t0.hour, t0.minute, t0.second)
			position, velocity = satellite.propagate(t0.year, t0.month, 5, hora, minuto, segundo)
			fechahora = datetime(t0.year,t0.month,t0.day,hora,minuto,segundo)
#			print "teme" , fechahora, position[0], position[1], position[2]
			r_tod = teme2tod(fechahora,position) 
#			print "tod" , fechahora, r_tod.item(0), r_tod.item(1), r_tod.item(2)
#			print "delta", fechahora, r_tod.item(0)-position[0] , r_tod.item(1)-position[1] , r_tod.item(2)-position[2]
#			dif = (r_tod.item(0)-position[0] , r_tod.item(1)-position[1] , r_tod.item(2)-position[2])
			dif = (xcods - r_tod.item(0) , ycods - r_tod.item(1) , zcods - r_tod.item(2))
			poscods = (xcods, ycods, zcods)
			velcods = (xpcods, ypcods, zpcods)
#			(v,n,c) = vncSis(position, velocity, dif)
			(v,n,c) = vncSis(poscods, velcods, dif)
			print fechahora, v,n,c
#print "fin"
