from subprocess import getstatusoutput as getout
from ase.io import read
from ase.units import Bohr
import os

# read structure
model = read('../0-scf/model.xyz')

# set temperature
temperature = model.info["temperature"]

# set electron_num
symbol2nele = {"H":1,"C":4,"N":5,"O":6}
electron_num = sum([symbol2nele[s] for s in model.symbols])

# set cell
cell = model.cell
#cell = cell*Bohr
latt0 = " ".join(list(map(str,cell[0].tolist())))
latt1 = " ".join(list(map(str,cell[1].tolist())))
latt2 = " ".join(list(map(str,cell[2].tolist())))

for title in ['h_pred','h_ref']:
    if not os.path.exists(f"{title}.csr"):
        continue

    # create work dir
    work_dir = os.path.join("./cond",f"cond-{title}")
    os.makedirs(work_dir,exist_ok=True)

    # write pyatb INPUT
    Input = f"""INPUT_PARAMETERS
{{
    nspin               1
    package             ABACUS
    fermi_energy        Auto
    fermi_energy_unit   Ry
    HR_route            ../../{title}.csr
    SR_route            ../../olp.csr
    rR_route            ../../rR.csr
    HR_unit             Ry
    rR_unit             Bohr
    max_kpoint_num      8000
}}

LATTICE
{{
    lattice_constant        {1/Bohr}
    lattice_constant_unit   Bohr
    lattice_vector
    {latt0}
    {latt1}
    {latt2}
}}

FERMI_ENERGY
{{
    temperature            {temperature}
    electron_num           {electron_num}
    grid                   25 25 25
    epsilon                1e-4
}}

BAND_STRUCTURE
{{
    wf_collect             0
    kpoint_mode            line
    kpoint_num             11
    high_symmetry_kpoint
    0.0000000000   0.0000000000   0.0000000000  100   # GAMMA          
    0.5000000000   0.0000000000   0.0000000000  100   # X              
    0.0000000000   0.5000000000   0.0000000000  100   # Y              
    0.0000000000   0.0000000000   0.0000000000  100   # GAMMA          
    0.0000000000   0.0000000000   0.5000000000  100   # Z              
   -0.5000000000  -0.5000000000   0.5000000000  100   # R_2            
    0.0000000000   0.0000000000   0.0000000000  100   # GAMMA          
    0.0000000000  -0.5000000000   0.5000000000  100   # T_2            
   -0.5000000000   0.0000000000   0.5000000000  100   # U_2            
    0.0000000000   0.0000000000   0.0000000000  100   # GAMMA          
    0.5000000000  -0.5000000000   0.0000000000    1   # V_2
}}

OPTICAL_CONDUCTIVITY
{{
    #occ_band      4
    omega         0   0.5
    domega        0.5
    eta           0.1
    grid          25 25 25
}}
"""
    with open(os.path.join(work_dir,"Input"),"w") as f:
        f.write(Input)

    # write jobfile
    jobfile = f"""#!/bin/bash
#SBATCH -N 1
#SBATCH --partition=p1
#SBATCH -n 40
#SBATCH --ntasks-per-node=40
#SBATCH --output=%j.out
#SBATCH --error=%j.err

export I_MPI_ADJUST_REDUCE=3
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1

ulimit -c 0

module purge
source /data/app/anaconda3/2024.10-1/etc/profile.d/conda.sh
conda activate pyatb
mpirun -n 40 pyatb
"""
    with open(os.path.join(work_dir,"jobfile"),"w") as f:
        f.write(jobfile)

    # sub jobfile
    cmd = f"cd {work_dir};sbatch jobfile"
    assert 0==os.system(cmd)
