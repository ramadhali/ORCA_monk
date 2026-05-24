from dataclasses import dataclass, replace
from itertools import product

@dataclass
class OrcaJob:
    """
    Data container holding all configuration switches for ORCA"""
    label: str = "SP"

    # Core calculation Switch
    opt: bool = False
    optts: bool = False
    freq: str | bool | None = False

    # Elctronic Calculation Switch
    functional: str = "HF"
    basis: str = "STO-3G"

    # Solvation Environment Parameters
    solvent: str | None = None
    solvent_model: str = "CPCM"

    # Numerical Integration Configurations
    grid: str | None = None
    extra_keywords: str = ""

    # Excited State Configurations
    tddft: bool = False
    nroots: int = 10
    iroot: int | None = None

    # Parallelization & Memory Controls
    nprocs: int = 1
    maxcore: int | str | None = None


# =================================
# Standalone Job Setting
# =================================

DEFAULT_SP=OrcaJob(
    label = "SP",
)

DEFAULT_FREQ=OrcaJob(
    label       = "FREQ",
    freq        = "analytical", # override in launch code
)

DEFAULT_OPT=OrcaJob(
    label       = "OPT",
    opt         = True,
)

DEFAULT_OPTTS=OrcaJob(
    label = "OPTTS",
    optts = True
)

# =================================
# Combined Job Setting
# =================================

DEFAULT_OPT_FREQ=replace(
    DEFAULT_OPT,
    label       = "OPT_FREQ",
    freq        = "analytical"
)

DEFAULT_OPTTS_FREQ=replace(
    DEFAULT_OPTTS,
    label       = "OPTTS_FREQ",
    freq        = "analytical"
)

# =================================
# Excited State Job Setting
# =================================

DEFAULT_TDDFT=OrcaJob(
    label       = "TDDFT",
    tddft       = True,
    functional  = "CAM-B3LYP",
    basis       = "def2-SVP",
)


DEFAULT_TDDFT_OPT=replace(
    DEFAULT_TDDFT,
    label       = "TDDFT_OPT",
    opt         = True,
    iroot       = 1,
)

DEFAULT_TDDFT_OPT_FREQ=replace(
    DEFAULT_TDDFT_OPT,
    label      = "TDDFT_OPT_FREQ",
    freq       = "analytical",
)

def make_job(base_job: OrcaJob, **overrides):    # override by user input
    return OrcaJob(
        **{**base_job.__dict__, **overrides}
    )


def build_orca_keywords(job: OrcaJob):
    # Normalize method flags to intercept all standard xTB config
    func_upper = job.functional.upper()
    is_xtb = "XTB" in func_upper or func_upper in ["GFN0", "GFN1", "GFN2", "GFN-FF"]
    parts=[]
    
    if is_xtb:
            parts.append(job.functional)
    else:
        parts.append(job.functional)
        parts.append(job.basis)
        # Force in-memory int calculation for standard DFT
        parts.append("Direct")

    if job.optts:
        parts.append("OptTS")
    elif job.opt:
        parts.append("OPT")
        
    if job.freq:
        if is_xtb or job.freq in ["numerical", "numfreq", "NumFreq"]:
        # numerical freq
            parts.append("NumFreq")
        elif job.freq in ["analytical", "freq", "FREQ", True]:
            parts.append("FREQ")



    if job.solvent is not None:
        parts.append(f"{job.solvent_model}({job.solvent})")

    if job.grid is not None and not is_xtb:
        parts.append(job.grid)

    if job.extra_keywords:
        parts.append(job.extra_keywords)

    return " ".join(parts)


def build_orca_optional_blocks(job: OrcaJob, TOTAL_MEMORY_ALLOCATION_MB):
    blocks=[]
    """
    job.maxcore is None     --> Skipping %maxcore, ORCA handles default
    job.maxcore == "auto"   --> maxcore ~ TOTAL_MEMORY_ALLOCATION_MB/nprocs
    job.maxcore is int      --> Manual override
    """
    
    if job.maxcore is None:
        pass
    elif str(job.maxcore).lower() == "auto":
        # TOTAL_MEMORY_ALLOCATION_MB/nprocs
        auto_maxcore=int(TOTAL_MEMORY_ALLOCATION_MB/job.nprocs)
        if job.nprocs == 1 and auto_maxcore > 8000:     # cap for single run
            auto_maxcore = 8000
        blocks.append(f"%maxcore {auto_maxcore}")
    
    else:
        blocks.append(f"%maxcore {int(job.maxcore)}")
    
    if job.nprocs > 1:
        blocks.append(f"%pal nprocs {job.nprocs} end")
    if job.tddft:
        iroot_part=f" iroot {job.iroot}" if job.iroot is not None else ""
        blocks.append(f"%tddft nroots {job.nroots}{iroot_part} end")

    # IN-RAM INTEGRAL CACHING (DISKLESS ENGINE)
#    blocks.append("%scf AOIntegrals Direct end")
#    blocks.append("%elprof\n  InCore True\nend")

    return "\n".join(blocks)

def make_jobs(base_job: OrcaJob,functionals,basis_sets,**overrides):
    jobs=[]
    for functional, basis in product(functionals,basis_sets):
        job=make_job(
            base_job,
            functional=functional,
            basis=basis,
            **overrides
        )
        jobs.append(job)
        
    return jobs