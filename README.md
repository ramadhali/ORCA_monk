# ORCA_monk

Modular ORCA + AiiDA workflow framework for quantum chemistry automation

## Features

- ORCA input generation from XYZ
- Modular ORCA parsers
- SCF / HOMO-LUMO parsing
- Optimization and frequency parsing
- Thermochemistry extraction
- AiiDA-based workflow execution
- Excel dataset generation

## Current Structure

```text
orca_io/	# ORCA input generation from .xyz to .inp
orca_jobs/	# ORCA job templates/settings (SP, OPT, FREQ, OPT_FREQ)
orca_parsers/	# ORCA output parsers (SCF, HOMO/LUMO, freq, thermochemistry)
```

## Planned Features

- Ionization potential workflows
- Transition-state workflows
- Reaction datasets
- TDDFT workflows
- ML-ready dataset generation

## Requirements

- ORCA
- AiiDA
- Python 3.14

## Job Templates

Default ORCA job templates are defined in

```
orca_jobs/orca_job_settings.py
```

Current templates include:

- DEFAULT_SP					(HF/STO-3G)
- DEFAULT_OPT				(HF/STO-3G)
- DEFAULT_FREQ				(HF/STO-3G)
- DEFAULT_OPT_FREQ			(HF/STO-3G)
- DEFAULT_TDDFT				(CAM-B3LYP/def2-SVP/nroots=10)
- DEFAULT_TDDFT_OPT			(CAM-B3LYP/def2-SVP/nroots=10)
- DEFAULT_TDDFT_OPT_FREQ	(CAM-B3LYP/def2-SVP/nroots=10/iroot=1)

### Changing Functional and Basis Set

Functionals and basis sets can be modified in:

```
launch_orca_aiida.py
```

Example:

```python
functionals = ["PBE0", "B3LYP"]
basis_sets = ["6-31g", "STO-3G", "def2-SVP"]
```

### Additional ORCA Settings

Additional ORCA settings can be passed through `make_jobs()`:

```python
jobs=[]
for template in job_templates:
    jobs.extend(
        make_jobs(
            template,
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


```

Supported options currently include:

- `label`			(used for ORCA input/output naming)
- `solvent`
- `solvent_model`
- `grid`
- `extra_keywords`	(for additional ORCA keywords e.g. `RIJCOSX`, `def2/J`)
- `nprocs`
- `maxcore`
- `nroots`
- `iroot`

Supported solvent models include:

- `CPCM`
- `COSMO`
- `SMD`
- `ALPB`

### Input Structures

Place `.xyz` files inside:

```
input_xyz/
```

## Usage

```bash
python3 launch_orca_aiida.py
```
