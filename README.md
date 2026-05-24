# ORCA_monk

Modular ORCA + AiiDA workflow framework for quantum chemistry automation.

## Features

- **Automated Input Generation**: Smooth transformation from raw `.xyz` coordinate geometries to fully configured `.inp` calculation records.
- **AiiDA Hybrid Execution Engine**: Dual-channel control via `USE_AIIDA_WORKFLOW` toggle. Runs jobs either locally as zero-overhead high-speed commands or wraps them into structural database records via `aiida-shell` with full graph provenance.
- **Method Compile Shield**: Automated interception of semi-empirical xTB functional variants (`GFN0`, `GFN1`, `GFN2`, `GFN-FF`) that strips conflicting orbital basis sets to prevent ORCA engine validation crashes.
- **Dynamic Multi-Mode Maxcore**: Intelligent memory management allocating core thresholds using `None` (native soft limit), `"auto"` (even thread balancing), or specific manual overrides.
- **Diskless Performance Caching**: Automatic top-line `Direct` formatting to lock intermediate integral computations straight into system RAM, completely shielding internal storage hard drives from intense `.tmp` file read/write traffic.
- **Symmetric Asset Harvester**: High-speed, low-overhead OS file cloning routing raw output matrices (`.out`, `.hess`, `.engrad`, `.xyz`) concurrently to structured excel trackers and dedicated subfolders.
- **Dual Verification Logging**: Simultaneous generation of isolated, permanent nested job bundles alongside a completely flat log sandbox.
- **Modular Data Parsers**: Detailed ground-state text parsing covering SCF metrics, HOMO/LUMO energies, analytical/numerical frequencies, and complete thermochemistry blocks.

## System Architecture

```text
.
├── README.md                 # Project documentation layout manual
├── launch_orca_aiida.py      # Main dashboard user controller loop entry point
├── runtime_config.py         # Cross-platform sentinel & macOS 4GB RAM disk mount utility
├── orca_aiida_runner.py      # Agnostic dual-channel local/AiiDA thread executor
├── orca_dataset.xlsx         # Consolidated spreadsheet record databank
├── test_parser.py            # Local diagnostic parser verification sandbox script
├── input_xyz/                # Working directory for raw incoming geometry files
├── orca_inp_from_xyz/        # Transient folder hosting generated ORCA inputs
├── debug_outputs/            # Flat tracking folder containing only standalone *.out logs
├── results/                  # Permanent home containing nested profile asset bundles
├── orca_io/                  # Input/Output core operations library pocket
│   ├── molecular_utils.py    # Chemical property solvers (weight, electrons, multiplicity)
│   ├── periodic_table.py     # Static elemental database reference ledger
│   ├── xyz_parser.py         # Geometry file character scanner
│   └── xyz_to_orca_inp.py    # Input file template block builder
├── orca_jobs/
│   └── orca_job_settings.py  # Unified blueprint registry, maxcore, and xTB compilers
├── orca_parsers/
│   └── orca_parser_gs.py     # Core ground-state log data extraction engine
└── tests/                    # Raw text assets for diagnostic parser checks
```

## Requirements

- **ORCA** (Verified for Version 6.1.1)
- **AiiDA** & **aiida-shell** (Optional, protected by lazy-loading function-level imports)
- **Python 3.10+** (Utilizes modern pipe union `|` type hints)
- **openpyxl**

## Job Templates

Default template objects are registered in `orca_jobs/orca_job_settings.py`:

| Template                   | Method Configuration | Key Task Variables                                                |
| :------------------------- | :------------------- | :---------------------------------------------------------------- |
| `DEFAULT_SP`             | HF/STO-3G            | Standalone Single Point Energy                                    |
| `DEFAULT_FREQ`           | HF/STO-3G            | Standalone Analytical Frequency (`freq="analytical"`)           |
| `DEFAULT_OPT`            | HF/STO-3G            | Geometry Optimization (`opt=True`)                              |
| `DEFAULT_OPTTS`          | HF/STO-3G            | Transition State Optimization (`optts=True`)                    |
| `DEFAULT_OPT_FREQ`       | HF/STO-3G            | Optimization + Analytical Freq Array                              |
| `DEFAULT_OPTTS_FREQ`     | HF/STO-3G            | Transition State Optimization + Numerical Freq Verification       |
| `DEFAULT_TDDFT`          | CAM-B3LYP/def2-SVP   | Excited State Response Loop (`tddft=True`, `nroots=10`)       |
| `DEFAULT_TDDFT_OPT`      | CAM-B3LYP/def2-SVP   | Excited State Structural Minimization (`opt=True`, `iroot=1`) |
| `DEFAULT_TDDFT_OPT_FREQ` | CAM-B3LYP/def2-SVP   | Excited State Optimization + Vibration Properties                 |

## Customisation Controls

### Workflow Mode Selector

Choose your graph-database tracking behavior at the top of `launch_orca_aiida.py`:

```python
# True  --> Loads your AiiDA profile and wraps runs via launch_shell_job()
# False --> Direct local bypass mode using standard background subprocess streams
USE_AIIDA_WORKFLOW = False
```

### Method Definition

Functionals, basis sets, charges, and spin multiplicities are enumerated directly in `launch_orca_aiida.py`:

```python
functionals = ["PBE0", "xtb", "gfn2-xtb"]
basis_sets = ["sto-3g", "def2-SVP"]
charges = [0]
multiplicities = ["auto"]
```

### Advanced Hardware & Infrastructure Overlay

Adjust cluster execution threads, solvent envelopes, integration configurations, and memory distribution directly inside the loop builder:

```python
jobs = []
for template in job_templates:
    jobs.extend(
        make_jobs(
            template,
            functionals,
            basis_sets,
            nprocs=4,          # Distribute workload across parallel execution threads
            maxcore="auto",    # "auto" splits TOTAL_MEMORY_ALLOCATION_MB evenly by nprocs
        
            # solvent="water",
            # solvent_model="CPCM",
            # grid="defgrid3",
            # extra_keywords="RIJCOSX def2/J",
        )
    )
```

### Hardware Allocation & RAM Safety Configuration

The framework is designed defensively to protect lower-spec machines from memory allocation crashes. If you or a tester are running calculations on a machine with a limited RAM footprint (e.g., an 8GB system), you must scale down the memory allocation pool variables at the top of `launch_orca_aiida.py` to match your hardware bounds before executing:

```python
# Hardware Core Memory Scales (Adjust based on your local system)
TOTAL_MEMORY_ALLOCATION_MB = 1500  # Scale down to ~1.5GB for a 2GB/8GB system pool
```

#### macOS Virtual RAM Disk Customisation

For macOS environments, the automatic virtual memory disk mount engine runs entirely behind the scenes inside **`runtime_config.py`**.

The storage capacity is defined using disk sectors (where 1 sector = 512 bytes). If your system is resource-constrained and cannot handle the default 4GB allocation, open **`runtime_config.py`** and modify line 100 inside the mount block to allocate a smaller chunk instead:

* **Default 4GB Allocation:** `ram_volume = 8388608` sectors.
* **Safe 2GB Allocation Downscale:** Change it to `ram_volume = 4194304` sectors.
* **Safe 1GB Allocation Downscale:** Change it to `ram_volume = 2097152` sectors.

```python
# Inside runtime_config.py -> auto_setup_orca_scratch_folders()
ram_volume = 4194304  # Allocates exactly 2GB (~2,048 MB) in volatile system memory
```


## Usage



To initiate pre-run environment validation, self-cleaning storage resets, memory caching mounts, and begin the calculation matrix sweep, run:

```bash
python3 launch_orca_aiida.py
```
