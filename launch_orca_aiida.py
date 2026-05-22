from pathlib import Path
from openpyxl import Workbook
from aiida import load_profile
from runtime_config import ORCA_EXECUTABLE, check_environment
from orca_jobs.orca_job_settings import make_jobs,DEFAULT_SP,DEFAULT_OPT,DEFAULT_FREQ,DEFAULT_OPT_FREQ

from orca_aiida_runner import run_orca,ORCA_DATASET_FIELDS
from orca_io.xyz_to_orca_inp import xyz_to_orca_inp
from itertools import product



# =======================
# DEFAULT_SP/OPT/FREQ/TDDFT/TDDFT_OPT/TDDFT_OPT/TDDFT_OPT_FREQ
# =======================
job_templates=[DEFAULT_SP,DEFAULT_OPT,DEFAULT_FREQ,DEFAULT_OPT_FREQ]     

functionals=["PBE0"]          # ["HF","B3LYP", "CAM-B3LYP"]
basis_sets=["sto-3g"]         # ["def2-svp", "sto-3g", "def2-tzvp"]



charges = [0]               # [-1, 0, 1]
multiplicities = [1]        # [1, 2, 3]

xyz_folder="input_xyz"          # input folder for *.xyz files
orca_inp_folder="orca_inp_from_xyz"  # folder to save $input.inp files
debug_folder="debug_outputs"    # folder to save $input##.out 

# =======================
# USER SETTINGS
# =======================
jobs=[]
for base_job in job_templates:
    jobs.extend(
        make_jobs(
            base_job,
            functionals,
            basis_sets,

            # solvent="water",
            # solvent_model="CPCM",
            # grid="DFGRID3",

            nprocs=4, 
            maxcore=4000,
            #
            #nroots=2,
            #iroot=1,
        )
    )


# =======================
# RUN WORKFLOW
# =======================

check_environment()

wb=Workbook()
ws=wb.active
ws.append(ORCA_DATASET_FIELDS)
ws.auto_filter.ref = ws.dimensions



for xyz_file,job,charge,multiplicity in product(
    Path(xyz_folder).glob("*.xyz"),
    jobs,
    charges,
    multiplicities,
):
    inp_file=xyz_to_orca_inp(xyz_file,
                          orca_inp_folder,
                          job,
                          charge,multiplicity,)
    node,properties=run_orca(inp_file,xyz_file.stem,job,charge,multiplicity,debug_folder,ORCA_EXECUTABLE,verbose=False)
    data=properties.get_dict()
    ws.append([data.get(h) for h in ORCA_DATASET_FIELDS])
    wb.save("orca_dataset.xlsx")
    print(f"Updated orca_dataset.xlsx for {xyz_file}")
