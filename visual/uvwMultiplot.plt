

## Coordenadas
set terminal postscript eps enhanced color 
set output 'vncmultiplot.eps'
set multiplot layout 3,1
set datafile separator ','
set grid
# Coordenada V
set title 'Along Track'
set ylabel 'Diferencias [km]'
set yrange[-2.0:1.0]
unset key
plot '../AjustarTLE/diferencias/difTotal' u 1:2 w p pt 1 lt 19
# Coordenada N
set title 'Radial'
unset key
set yrange[-0.1:0.2]
plot '../AjustarTLE/diferencias/difTotal' u 1:3 w p pt 1 lt 12
# Coordenada C
set title 'Cross Track'
unset key
set yrange[-0.5:0.5]
plot '../AjustarTLE/diferencias/difTotal' u 1:4  w p pt 1 lt 7
unset multiplot










