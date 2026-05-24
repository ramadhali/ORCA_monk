import os
import platform
import subprocess
from pathlib import Path
import shutil



# ===================================================
# Checking if all packages are available: ORCA, AiiDA
#====================================================

# orca needs full path for MPI run
ORCA_EXECUTABLE=Path("/Users/rama/Library/orca_6_1_1/orca")

def check_orca():
    if not ORCA_EXECUTABLE.exists():
        raise FileNotFoundError(f"ORCA executable not found: {ORCA_EXECUTABLE}")
    if not ORCA_EXECUTABLE.is_file():
        raise FileNotFoundError(f"ORCA path is not a file: {ORCA_EXECUTABLE}")
    print(f"ORCA executable found: {ORCA_EXECUTABLE}")

#AiiDA import shield: for Beta-test, activates USE_AIIDA=FALSE if load.profile() fails
try:
    from aiida import load_profile
    AIIDA_PROFILE_AVAILABLE = True
except ImportError:
    AIIDA_PROFILE_AVAILABLE = False
    load_profile = None



def check_aiida(force_check=True):
    # overrule force_check if AiiDA is not installed in machine
    if not AIIDA_PROFILE_AVAILABLE:
        print("AiiDA not found...skipping environmental validation")
        return False
    if force_check:
        try:
            load_profile()
            print("Aiida profile loaded succesfully")
            return True
        except Exception as e:
            print (f"Failed to establish active AiiDA framework: (Local Bypass activated) {e}")
            return False
    return False






# Set scratch folder for system memory
def universal_orca_scratch_space(RAM_disk):
    """ADAPTIVE PLATFORM CHOCIE 
    Autumatically locates the fastest available system memory path on any os"""
    current_os = platform.system().lower()

    if current_os == "darwin":      #macOS
        ram_disk = Path(f"/Volumes/{RAM_disk}")
        return ram_disk if ram_disk.exists() else None
    
    elif current_os == "linux":     # Linux/Ubuntu
        ram_disk = Path("/dev/shm")
        return ram_disk if ram_disk.exists() else None
    elif current_os == "windows":   # Wisdows
        # Windows handles memory cache implicitly; direct fallback is better
        return None
    
def auto_setup_orca_scratch_folders(RAM_disk, orca_inp_folder, results_folder, debug_folder):
    print("=== System Initialization ===")

    #wipe out previous generated input and result/debug folder
    for target_folder in [orca_inp_folder,results_folder,debug_folder]:
        folder_path=Path(target_folder)
        if folder_path.exists():
            print(f"cleaning old workspace: {target_folder}")
            try:
                shutil.rmtree(folder_path)
            except Exception as e:
                print(f"Warning: Couldn't fully clear {target_folder}")


    Path(orca_inp_folder).mkdir(parents=True, exist_ok=True)
    Path(results_folder).mkdir(parents=True,exist_ok=True)
    Path(debug_folder).mkdir(parents=True, exist_ok=True)
    """Mac does not keep the created volumes after restart
    so we need to create it everytime it restart"""

    if platform.system().lower() == "darwin":
        
        ram_disk_path=Path(f"/Volumes/{RAM_disk}")
        if not ram_disk_path.exists():
            print("MacOS alert: Ultra-fast RAM disk not found. attempting auto-mount...")
            try:
                ram_volume = 8388608  # in bytes ~ 4GB
                mound_cmd=f"diskutil erasevolume HFS+ '{RAM_disk}' `hdiutil attach -nomount ram://{ram_volume}`"
                subprocess.run(
                    mound_cmd,
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
                if ram_disk_path.exists():
                    print(f"RAM Disk mounted in memory at: {RAM_disk}")
            except Exception as e:
                print(f"Warning: Auto-mount failed. Using local SSD")
        else:
            print(f"Active RAM Disk verified in memory at: {RAM_disk}")
    print("========================")

def check_environments(verify_aiiada_profile,RAM_disk,orca_inp_folder,results_folder,debug_folder):
    check_orca()
    aiida_active=check_aiida(force_check=verify_aiiada_profile)
    auto_setup_orca_scratch_folders(RAM_disk,orca_inp_folder,results_folder,debug_folder)
    return aiida_active

