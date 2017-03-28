# TODO JUNTO
set title 'Diferencias LAGEOS ESC-11'
set xlabel 'Diferencia Temporal [dias]'
set ylabel 'Diferencia[km]'
#set xdata time
set grid
set datafile separator ','
#set timefmt '%Y-%m-%d %H:%M:%S'
#set xrange ['2003-03-16 15:00':'2003-03-01 13:00']
#set format x "%b %d\n%H:%M"
plot '../AjustarTLE/diferencias/difTotal' u 1:2 title 'Cross-track' w p pt 1 lt 7, '../AjustarTLE/diferencias/difTotal' u 1:3 title 'Velocity (in-track)' w p pt 1 lt 19 , '../AjustarTLE/diferencias/difTotal' u 1:4 title 'Normal (along-radial)' w p pt 1 lt 12
set terminal postscript eps enhanced color font 'Helvetica,10'
set output 'Scenario11.eps'
replot
set term x11
pause 15
