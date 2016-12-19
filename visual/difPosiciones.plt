# TODO JUNTO
set title 'Diferencias'
set xlabel 'Fecha y Hora'
set ylabel 'Diferencia[km]'
set xdata time
set datafile separator ','
set timefmt '%Y-%m-%d %H:%M:%S'
set xrange ['2003-10-12 13:00':'2003-09-27 15:00']
set format x "%b %d\n%H:%M"
plot '../AjustarTLE/diferencias/difTotal0' u 5:4 title 'Cross-track' w p pt 1 lt 7, '../AjustarTLE/diferencias/difTotal0' u 5:3 title 'Velocity (in-track)' w p pt 1 lt 19 , '../AjustarTLE/diferencias/difTotal0' u 5:2 title 'Normal (along-radial)' w p pt 1 lt 12
set terminal postscript eps enhanced color font 'Helvetica,10'
set output 'Scenario43.eps'
replot
set term x11
pause 10
