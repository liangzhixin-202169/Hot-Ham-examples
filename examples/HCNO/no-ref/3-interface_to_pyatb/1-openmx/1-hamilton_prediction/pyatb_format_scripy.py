import sys
import json5
from hotham.tools.hamiltonian_calc import Hamiltonian_Calc
from hotham.tools.topyatb import ToPyatb
if __name__ == '__main__':
    with open(sys.argv[1], "r") as f:
        inputfile = json5.load(f)
    #hamil_calc = Hamiltonian_Calc(inputfile)
    #hamil_calc.run()
    topyatb = ToPyatb(inputfile)
    topyatb.run()
