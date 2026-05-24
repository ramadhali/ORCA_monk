import time
import subprocess
from pathlib import Path
import shutil
import platform     # Native platform detection library

from orca_jobs.orca_job_settings import OrcaJob, build_orca_keywords
from orca_parsers.orca_parser_gs import parse_orca_output
from runtime_config import universal_orca_scratch_space


ORCA_DATASET_FIELDS = [
        "molecule",
        "label",
        "functional",
        "basis",
        "solvent",
        "solvent_model",
        "grid",
        "extra_keywords",
        "tddft",
        "nroots",
        "iroot",
        "nprocs",
        "maxcore",
        "orca_keywords",
        "charge",
        "multiplicity",
        "final_energy_hartree",
        "normal_termination",
        "optimization_converged",
        "optimization_cycles",
        "n_frequencies",
        "n_imaginary_frequencies",
        "lowest_frequency_cm-1",
        "HOMO_eV",
        "LUMO_eV",
        "gap_eV",
        "zero_point_energy_hartree",
        "enthalpy_hartree",
        "gibbs_free_energy_hartree",
        "calculation_pk",
        "runtime_seconds",
    ]


class MockAiiDANODE:
    """Mode node mirroring AiiDA's node object for direct loacl Bypass"""
    def __init__(self,pk=0): self.pk=pk

class MockAiiDADICT:
    """Mock Dict mirroring AiiDA's Dict object for direct local Bypass"""
    def __init__(self,data_dict): self._data=data_dict; self.pk=0
    def get_dict(self): return self._data
    def store(self): return self



def run_orca(
        input_filename,
        job_profile_name,
        job: OrcaJob,   # SP/OPT/FREQ
        charge,
        multiplicity,
        results_folder,
        debug_folder,
        orca_executable,
        verbose=True,
        use_aiida=False
    ):
    

    #start time stamp
    start_time=time.time()
    input_path=Path(input_filename).resolve()

    # Permanent results directories
    results_folder_dir=Path(results_folder) / job_profile_name
    results_folder_dir.mkdir(parents=True, exist_ok=True)

    # debug folder
    debug_folder_dir=Path(debug_folder)
    debug_folder_dir.mkdir(parents=True, exist_ok=True)

    molecular_base_name=job_profile_name.split("_")[0]

    # AiiDA setup
    if use_aiida:
        from aiida_shell import launch_shell_job
        from aiida.orm import SinglefileData
    
        input_file=SinglefileData(file=input_path)
        result,node=launch_shell_job(
            "bash",
            arguments=["-c",f"{orca_executable} orca.inp > orca.out"],
            nodes={"orca_inp":input_file},
            filenames={"orca_inp":"orca.inp"},
            outputs=["orca.out"]
        )
        orca_out_text=result["orca_out"].get_content()
        calc_pk=node.pk

    else:
        # Mode B: Direct local high-speed command line execution
        scatch_base=universal_orca_scratch_space(Path(results_folder).name)
        run_dir=(scatch_base if scatch_base is not None else input_path.parent) / f"local_run_{int(start_time)}"
        run_dir.mkdir(parents=True, exist_ok=True)
        # If sratch folder is present

        local_inp=run_dir / "orca.inp"
        local_out=run_dir / "orca.out"
        local_inp.write_text(input_path.read_text())

        is_windows = platform.system().lower() == "windows"

        with open (local_out, "w") as f:
            subprocess.run(
                [str(orca_executable), "orca.inp"],
                cwd=run_dir,
                stdout=f,
                stderr=subprocess.PIPE,
                shell=is_windows
            )

        if local_out.exists():
            orca_out_text=local_out.read_text()     # orca_out file
            output_collection_extentions = [".hess", ".engrad", ".xyz"]
            for output_collection_extention in output_collection_extentions:
                orca_output_collection=run_dir / f"orca{output_collection_extention}"
                if orca_output_collection.exists():
                    save_orca_output_collection=results_folder_dir / f"{job_profile_name}{output_collection_extention}"
                    shutil.copy2(orca_output_collection, save_orca_output_collection)
            shutil.copy2(input_path, results_folder_dir/f"{job_profile_name}.inp")
        else:
            orca_out_text="Error: ORCA output file generation failed"
        
        node = MockAiiDANODE(pk=0)
        calc_pk=0

        # Clean scratch binary
        try:
            shutil.rmtree(run_dir)
        except Exception:
            pass

    # end time
    runtime_seconds=time.time()-start_time
    
    # save output file for logging and verification
    with open(results_folder_dir / f"{job_profile_name}.out", "w") as f:
        f.write(orca_out_text)
    shutil.copy2(results_folder_dir/f"{job_profile_name}.out", debug_folder_dir/f"{job_profile_name}.out")
    
    # Parsing files
    orca_parsed_output=parse_orca_output(orca_out_text)

    # create dataset_row
    dataset_row = build_orca_dataset_row(
        orca_parsed_output,
        molecular_base_name,
        job,
        charge,
        multiplicity,
        calc_pk,
        runtime_seconds,
    )

    #store in Dict for aiida
    if use_aiida:
        from aiida.orm import Dict
        properties=Dict(dict=dataset_row).store()
    else:
        properties = MockAiiDADICT(dataset_row)

    if verbose:
        print("Calculation pk",node.pk)
        print("properties pk",properties.pk)
        print(
            f"{molecular_base_name} | {job.label} | "
            f"{dataset_row['orca_keywords']} | "
            f"q={charge} m={multiplicity} | "
            f"energy={dataset_row['final_energy_hartree']} | "
            f"runtime={runtime_seconds:.2f}s"
        )   
    return node,properties


# to create dataset_row for both orca_parsed_output and workbook
def build_orca_dataset_row(
        orca_parsed_output,
        molecule,
        job: OrcaJob,
        charge,
        multiplicity,
        calc_pk,
        runtime_seconds,
):
    row = dict(orca_parsed_output)
    row["molecule"] = molecule
    row["label"] = job.label
    row["functional"] = job.functional
    row["basis"] = job.basis
    row["solvent"] = job.solvent
    row["solvent_model"] = job.solvent_model
    row["grid"] = job.grid
    row["extra_keywords"] = job.extra_keywords
    row["tddft"] = job.tddft
    row["nroots"] = job.nroots
    row["iroot"] = job.iroot
    row["nprocs"] = job.nprocs
    row["maxcore"] = job.maxcore
    row["orca_keywords"] = build_orca_keywords(job)
    row["charge"] = charge
    row["multiplicity"] = multiplicity
    row["calculation_pk"] = calc_pk
    row["runtime_seconds"] = runtime_seconds

    return row
