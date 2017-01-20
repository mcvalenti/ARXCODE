#set title 'Diferencia de Coordenadas entre los TLE y los datos CODS'
set terminal postscript eps enhanced color font 'Helvetica,10'
set output 'diferenciasTOD.eps'
set multiplot
set size 1,.3
set ylabel 'km'
set xdata time
set datafile separator ' '
set timefmt '%Y-%m-%d'
set xrange ['2013-11-01':'2013-12-30']
set yrange [-1:4]
set format x "%m-%d"
set origin 0,0
h(x)=e*x+f
fit h(x) '../Comparar/diferenciasTOD' u 1:3 via e,f
plot '../Comparar/diferenciasTOD' u 1:3 title 'Coordenada X', h(x)
set origin 0,.3
g(x)=c*x+d
fit g(x) '../Comparar/diferenciasTOD' u 1:4 via c,d
plot '../Comparar/diferenciasTOD' u 1:4 title 'Coordenada Y' , g(x)
set origin 0,.6
f(x)=a*x+b
fit f(x) '../Comparar/diferenciasTOD' u 1:5 via a,b
plot '../Comparar/diferenciasTOD' u 1:5 title 'Coordenada Z', f(x)
unset multiplot
unset output
set term x11
pause 10