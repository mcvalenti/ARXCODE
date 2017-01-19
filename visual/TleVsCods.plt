set title 'Diferencia de Coordenadas entre los TLE y los datos CODS'
set xlabel 'Fecha'
set ylabel 'Diferencia en km'
set xdata time
set datafile separator ' '
set timefmt '%Y-%m-%d'
set xrange ['2013-11-01':'2013-12-30']
set format x "%m-%d"
#plot '../Comparar/diferenciasTOD' u 1:3 title 'Coordenada X'
#plot '../Comparar/diferenciasTOD' u 1:4 title 'Coordenada Y' 
plot '../Comparar/diferenciasTOD' u 1:5 title 'Coordenada Z' 
set terminal postscript eps enhanced color font 'Helvetica,10'
set output 'diferenciasTOD.eps'
replot
set term x11
pause 10