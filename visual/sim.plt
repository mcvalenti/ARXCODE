set title 'Diferencias'
set xlabel 'Fecha y Hora'
set ylabel 'Diferencia[km]'
set xdata time
set datafile separator ','
set timefmt '%Y-%m-%d %H:%M:%S'
set xrange ['2014-01-15 13:00':'2014-01-22 15:00']
set format x "%b %d\n%H:%M"
plot '../AjustarTLE/diferencias/difTotal0' u 5:2 
set terminal postscript eps enhanced color font 'Helvetica,10'
set output 'diferenciasGraficos.eps'
replot
set term x11


