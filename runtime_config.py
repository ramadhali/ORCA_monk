from pathlib import Path
from aiida import load_profile

# checking if all packages are available: ORCA, AiiDA
# orca needs full path for MPI run
ORCA_EXECUTABLE=Path("/Users/rama/Library/orca_6_1_1/orca")

def check_orca():
    if not ORCA_EXECUTABLE.exists():
        raise FileNotFoundError(f"ORCA executable not found: {ORCA_EXECUTABLE}")
    if not ORCA_EXECUTABLE.is_file():
        raise FileNotFoundError(f"ORCA path is not a file: {ORCA_EXECUTABLE}")
    print(f"ORCA executable found: {ORCA_EXECUTABLE}")

def check_aiida():
    load_profile()
    print("Aiida profile loaded succesfully")


def check_environment():
    check_orca()
    check_aiida()