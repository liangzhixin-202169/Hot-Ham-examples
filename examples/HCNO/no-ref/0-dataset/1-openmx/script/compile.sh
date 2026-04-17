module purge
module load openmx/3.9-patch3.9.9-intel2023.2
CC="mpicc -O3 -fopenmp"
$CC openmx2hotham.c read_scfout.c -o openmx2hotham 

