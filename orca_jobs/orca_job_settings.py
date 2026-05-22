from dataclasses import dataclass
from itertools import product

@dataclass
class OrcaJob:
    label: str = "SP"

    opt: bool = False
    freq: bool = False

    functional: str = "HF"
    basis: str = "STO-3G"

    solvent: str | None = None
    solvent_model: str | None = None

    grid: str | None = None
    extra_keywords: str = ""

    tddft: bool = False
    nroots: int = 10
    iroot: int | None = None

    nprocs: int = 1
    maxcore: int | None = None




COMMON_DEFAULTS={
    "opt": False,
    "freq": False,

    "functional": "HF",
    "basis": "STO-3G",

    "solvent": None,
    "solvent_model": "CPCM",

    "grid": None,
    "extra_keywords": "",

    "tddft": False,
    "nroots":10,
    "iroot": None,

    "nprocs": 1,
    "maxcore": None,
}

DEFAULT_SP={
    "label": "SP",
}

DEFAULT_FREQ={
    "label": "FREQ",
    "freq": True,
}

DEFAULT_OPT={
    "label": "OPT",
    "opt": True,
}
DEFAULT_OPT_FREQ={
    **DEFAULT_OPT,
    "label": "OPT_FREQ",
    "freq": True
}

DEFAULT_TDDFT={
    "tddft": True,
    "label": "TDDFT",
    "functional": "CAM-B3LYP",
    "basis": "def2-SVP",
}


DEFAULT_TDDFT_OPT={
    **DEFAULT_TDDFT,
    "label":"TDDFT_OPT",

    "opt": True,
    "iroot": 1,
}

DEFAULT_TDDFT_OPT_FREQ={
    **DEFAULT_TDDFT_OPT,
    "label": "TDDFT_OPT_FREQ",
    "freq": True,
}

def make_job(job_defaults,**overrides):
    job=COMMON_DEFAULTS.copy()  #copy default
    job.update(job_defaults)    #replace with SP/OPT if DEFAULT_SP/DEFAULT_OPT is choosen
    job.update(overrides)       # replace with human input
    return job

def build_orca_keywords(job):
    parts=[
        job["functional"],
        job["basis"],
    ]

    if job["opt"]:
        parts.append("OPT")
    if job["freq"]:
        parts.append("FREQ")

    if job["solvent"] is not None:
        parts.append(f"{job['solvent_model']}({job['solvent']})")
    if job["grid"] is not None:
        parts.append(job["grid"])
    if job["extra_keywords"]:
        parts.append(job["extra_keywords"])
    return " ".join(parts)


def build_orca_optional_blocks(job):
    blocks=[]

    if job["maxcore"] is not None:
        blocks.append(f"%maxcore {job['maxcore']}")
    
    if job["nprocs"] > 1:
        blocks.append(f"%pal nprocs {job['nprocs']} end")
    if job["tddft"]:
        iroot_part=f" iroot {job['iroot']}" if job["iroot"] is not None else ""
        blocks.append(f"%tddft nroots {job['nroots']}{iroot_part} end")
    return "\n".join(blocks)

def make_jobs(job_template,functionals,basis_sets,**overrides):
    jobs=[]
    for functional, basis in product(functionals,basis_sets):
        job=make_job(job_template,functional=functional,basis=basis,**overrides)
        jobs.append(job)
        
    return jobs