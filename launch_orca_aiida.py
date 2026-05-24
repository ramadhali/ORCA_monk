from pathlib import Path
from openpyxl import Workbook
from aiida import load_profile
from runtime_config import ORCA_EXECUTABLE, check_environments
from orca_jobs.orca_job_settings import make_jobs,DEFAULT_SP,DEFAULT_OPT,DEFAULT_FREQ,DEFAULT_OPT_FREQ

from orca_aiida_runner import run_orca,ORCA_DATASET_FIELDS
from orca_io.xyz_to_orca_inp import xyz_to_orca_inp
from itertools import product


# ===================================================================
# HARDWARE & RUNTIME CONTROLS
# ===================================================================
USE_AIIDA_WORKFLOW = False # switch to False for direct ORCA launch
TOTAL_MEMORY_ALLOCATION_MB = 10240  # 10GB
RAM_disk="orca_monk_ram_disk"

# ===================================================================
# DIRECTORIES CONTROLS
# ===================================================================
xyz_folder="input_xyz"                  # input folder for *.xyz files
orca_inp_folder="orca_inp_from_xyz"     # folder to save $input.inp files
results_folder="results"                # nested output file
debug_folder="debug_outputs"            # folder to save $input##.out 

# ===================================================================
# JOB TEMPLATES CONFIGURATION
# ===================================================================
job_templates=[DEFAULT_SP,DEFAULT_OPT,DEFAULT_FREQ,DEFAULT_OPT_FREQ]     

functionals=["pbe0"]          # ["HF","B3LYP", "CAM-B3LYP"]
basis_sets=["sto-3g"]         # ["def2-svp", "sto-3g", "def2-tzvp"]

charges = [0]               # [-1, 0, 1]
multiplicities = [1]        # [1, 2, 3]

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
            maxcore="auto",   # automacatally estimated by: nprocs/TOTAL_MEMORY_ALLOCATION_MB in orca_io/orca_job_settings.py
            #
            #nroots=2,
            #iroot=1,
        )
    )

# ===================================================================
# RUN TIME ENVIRONMENT AUTO-INITIALIZATION
# ===================================================================

# AiiDA checking
aiida_status=check_environments(
    USE_AIIDA_WORKFLOW,
    RAM_disk,
    orca_inp_folder,
    results_folder,
    debug_folder)
USE_AIIDA_WORKFLOW = aiida_status

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
    solvent_name=job.solvent if job.solvent is not None else "gas"
    job_profile_name=f"{xyz_file.stem}_{job.label}_{job.functional}_{job.basis}_{solvent_name}_q{charge}_m{multiplicity}"
    
    inp_file=xyz_to_orca_inp(xyz_file,
                          orca_inp_folder,
                          job,
                          charge,
                          multiplicity,
                          job_profile_name,
                          TOTAL_MEMORY_ALLOCATION_MB)
    # Launch the job here
    node,properties=run_orca(
        inp_file,
        job_profile_name,
        job,
        charge,
        multiplicity,
        results_folder,
        debug_folder,
        ORCA_EXECUTABLE,
        verbose=False,
        use_aiida=USE_AIIDA_WORKFLOW)
    
    data=properties.get_dict()
    ws.append([data.get(h) for h in ORCA_DATASET_FIELDS])
    wb.save("orca_dataset.xlsx")
    mode_tag="AiiDA Mode" if USE_AIIDA_WORKFLOW else "Local Bypass"
    print(f"[{mode_tag}] Updated orca_dataset.xlsx | {xyz_file.stem} | {job.label} | q={charge} | m={multiplicity} | runtime={data['runtime_seconds']:.2f}s")


