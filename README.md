# Quantum Repeater Superconducting Qubit PDK
## Process Design Kit — Version 2.1.0

### Overview
This PDK provides a complete design environment for superconducting qubit-based
quantum repeater nodes. It targets aluminum-on-silicon (Al/Si) and
niobium-on-silicon-nitride (Nb/SiN) fabrication processes optimized for:

- **Transmon qubits** (fixed-frequency and tunable)
- **Josephson Junction arrays** (Manhattan & Dolan bridge geometry)
- **Coplanar Waveguide (CPW) resonators** (readout & memory)
- **SQUID tunable couplers**
- **Purcell filters**
- **Quantum memory interface pads**
- **Entanglement generation Bell-state measurement (BSM) circuits**
- **Classical control routing** (flux bias, microwave drive, DC lines)

### Compatibility
| Tool         | Version  | Notes                          |
|--------------|----------|--------------------------------|
| GDSFactory   | ≥ 7.x    | Primary layout engine          |
| KLayout      | ≥ 0.28   | DRC, LVS, visualization        |
| Qucs-S       | ≥ 24.x   | Circuit simulation             |
| QuTiP        | ≥ 5.x    | Hamiltonian / Lindblad sim     |
| ANSYS HFSS   | ≥ 2023   | EM field simulation            |
| Sonnet       | ≥ 18.x   | Planar EM (CPW)                |
| OpenEMS      | latest   | Open-source FDTD               |
| AWR/Microwave Office | any | RF circuit sim              |

### Directory Structure
```
quantum_repeater_pdk/
├── README.md                    ← This file
├── pdk_config.yaml              ← PDK global configuration
├── tech/
│   ├── process_stack.yaml       ← Fabrication layer stack
│   ├── layer_map.yaml           ← GDS layer numbers
│   └── material_properties.yaml ← εr, tan δ, sheet resistance
├── design_rules/
│   ├── drc_rules.yaml           ← Design rule constraints
│   ├── drc_klayout.lydrc        ← KLayout DRC script
│   └── lvs_rules.yaml           ← Layout vs Schematic rules
├── primitives/
│   ├── josephson_junction.py    ← JJ cell (Manhattan/Dolan)
│   ├── squid.py                 ← DC-SQUID / rf-SQUID
│   ├── transmon_qubit.py        ← Transmon qubit cell
│   ├── cpw_resonator.py         ← CPW λ/4 and λ/2 resonators
│   ├── purcell_filter.py        ← Purcell bandpass filter
│   ├── flux_bias_line.py        ← On-chip flux bias coupler
│   ├── drive_line.py            ← Microwave drive port
│   └── capacitor_pads.py        ← Interdigital & parallel-plate caps
├── cells/
│   ├── qubit_cell.py            ← Single transmon cell assembly
│   ├── readout_cell.py          ← Readout resonator + Purcell
│   ├── coupler_cell.py          ← Tunable SQUID coupler
│   ├── bsm_cell.py              ← Bell-state measurement cell
│   ├── memory_interface.py      ← Quantum memory bus interface
│   └── repeater_node.py         ← Full repeater node top-level
├── models/
│   ├── spice/
│   │   ├── jj_rcsj.cir          ← RCSJ Josephson junction model
│   │   ├── transmon.cir         ← Transmon circuit model
│   │   ├── cpw_resonator.cir    ← Distributed CPW model
│   │   └── repeater_circuit.cir ← Top-level repeater schematic
│   ├── hamiltonian/
│   │   ├── transmon_ham.py      ← Transmon Hamiltonian (QuTiP)
│   │   ├── qubit_resonator.py   ← Jaynes-Cummings / dispersive
│   │   └── repeater_ham.py      ← Full repeater Hamiltonian
│   └── em/
│       ├── hfss_setup.py        ← ANSYS HFSS automation
│       └── sonnet_setup.py      ← Sonnet project template
├── simulations/
│   ├── sim_config.yaml          ← Simulation parameters
│   ├── run_drc.py               ← DRC runner script
│   └── run_em_sweep.py          ← EM parameter sweep
├── scripts/
│   ├── generate_gds.py          ← GDS export script
│   └── validate_pdk.py          ← PDK integrity checker
└── docs/
    ├── design_guide.md          ← Designer's guide
    └── fab_spec.md              ← Fabrication specification
```

### Quick Start
```python
import sys
sys.path.insert(0, "quantum_repeater_pdk")

from cells.repeater_node import RepeaterNode

node = RepeaterNode(
    n_qubits=4,
    process="Al_Si_150nm",
    qubit_freq_GHz=[4.8, 5.1, 5.4, 5.7],
    readout_freq_GHz=[6.5, 6.7, 6.9, 7.1],
)
gds = node.build()
gds.write_gds("repeater_node.gds")
```

### License
Academic / Research use. See LICENSE for details.
