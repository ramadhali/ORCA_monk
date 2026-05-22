from dataclasses import dataclass, replace
from itertools import product

@dataclass
class OrcaJob:
    label: str = "SP"

    opt: bool = False
    freq: bool = False

    functional: str = "HF"
    basis: str = "STO-3G"

    solvent: str | None = None
    solvent_model: str = "CPCM"

    grid: str | None = None
    extra_keywords: str = ""

    tddft: bool = False
    nroots: int = 10
    iroot: int | None = None

    nprocs: int = 1
    maxcore: int | None = None




DEFAULT_SP=OrcaJob(
    label = "SP",
)

DEFAULT_FREQ=OrcaJob(
    label       = "FREQ",
    freq        = True,
)

DEFAULT_OPT=OrcaJob(
    label       = "OPT",
    opt         = True,
)

DEFAULT_OPT_FREQ=replace(
    DEFAULT_OPT,
    label       = "OPT_FREQ",
    freq        = True
)

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
    freq       = True,
)

def make_job(base_job: OrcaJob, **overrides):    # override by user input
    return OrcaJob(
        **{**base_job.__dict__, **overrides}
    )


def build_orca_keywords(job: OrcaJob):
    parts=[
        job.functional,
        job.basis,
    ]

    if job.opt:
        parts.append("OPT")
    if job.freq:
        parts.append("FREQ")

    if job.solvent is not None:
        parts.append(f"{job.solvent_model}({job.solvent})")

    if job.grid is not None:
        parts.append(job.grid)

    if job.extra_keywords:

        parts.append(job.extra_keywords)
    return " ".join(parts)


def build_orca_optional_blocks(job: OrcaJob):
    blocks=[]

    if job.maxcore is not None:
        blocks.append(f"%maxcore {job.maxcore}")
    
    if job.nprocs > 1:
        blocks.append(f"%pal nprocs {job.nprocs} end")
    if job.tddft:
        iroot_part=f" iroot {job.iroot}" if job.iroot is not None else ""
        blocks.append(f"%tddft nroots {job.nroots}{iroot_part} end")
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