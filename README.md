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

## Usage

`python3 launch_orca_aiida.py`
