"""
72-Qubit Superconducting Quantum Repeater
GDS Architecture Specification
==============================================
Generate: python3 gen_qr72.py
Output  : QR72_quantum_repeater.gds
"""

# ══════════════════════════════════════════
#  CHIP SUMMARY
# ══════════════════════════════════════════

CHIP = {
    "name":           "QR72 — 72-Qubit Quantum Repeater",
    "total_qubits":   72,
    "nodes":          3,
    "qubits_per_node":24,
    "chip_size_um":   "12500 × 6500",
    "substrate":      "Si (intrinsic, >10 kΩ·cm, 525 µm)",
    "base_metal":     "Nb (200 nm, DC sputter)",
    "junction":       "Al/AlOx/NbTiN (shadow evap)",
    "operating_T_mK": 15,
    "gds_cells":      21,
    "gds_polygons":   "7,358 (+ 491 cell references)",
    "gds_file_kb":    1377,
}

# ══════════════════════════════════════════
#  NODE ARCHITECTURE (× 3)
# ══════════════════════════════════════════

NODE = {
    "size_um":      "3800 × 5800",
    "qubit_count":  24,
    "layout": {
        "memory_qubits": {
            "count": 8, "arrangement": "2 rows × 4 cols",
            "cell": "XMON_MEM",
            "freq_GHz": "4.5–5.0",
            "T1_target_us": 200,
            "T2_target_us": 300,
            "use": "Quantum memory: stores entanglement between BSM rounds",
            "pitch_um": "700 (x) × 800 (y)",
        },
        "bsm_qubits": {
            "count": 8, "arrangement": "2 rows × 4 cols (flanking memory)",
            "cell": "XMON_BSM",
            "freq_GHz": "5.0–5.5",
            "T1_target_us": 100,
            "use": "Bell-state measurement: joint measurement for entanglement swapping",
            "pitch_um": "650 (x) × 750 (y)",
        },
        "entanglement_qubits": {
            "count": 4, "arrangement": "2 left edge + 2 right edge",
            "cell": "XMON_ENT",
            "freq_GHz": "5.5–6.0",
            "T1_target_us": 50,
            "use": "Microwave-optical transducer interface; generates remote entanglement",
            "transducer": "TRANSDUCER_PAD (400×400 µm)",
        },
        "tunable_couplers": {
            "count": 4,
            "cell": "XMON_TC",
            "freq_GHz": 7.0,
            "use": "Flux-tunable coupling (0–30 MHz) between memory and BSM qubits",
            "jj_cell": "JJ_COUPLER",
        },
        "readout_resonators": {
            "count": 12,  # 8 memory + 4 BSM (shared)
            "cell": "RESONATOR",
            "freq_GHz": 7.0,
            "Q_loaded": 5000,
            "length_um": 4800,
        },
        "flux_lines": {
            "count": 24,
            "cell": "FLUX_LINE",
            "mutual_inductance_pH": 2.0,
            "max_current_mA": 2.0,
        },
        "airbridges": {
            "spacing_um": 200,
            "cell": "AIRBRIDGE",
            "purpose": "Suppress parasitic slot-mode resonances in CPW",
        },
    }
}

# ══════════════════════════════════════════
#  QUBIT ELECTRICAL TARGETS
# ══════════════════════════════════════════

QUBIT_TARGETS = {
    "XMON_MEM": {
        "cross_width_um":  20,  "cross_length_um": 200, "cross_gap_um": 20,
        "freq_GHz":        4.75, "anharmonicity_MHz": -200,
        "EJ_GHz":          15.2, "EC_MHz": 200, "EJ_EC": 76,
        "Ic_nA":           50,   "Rn_kOhm": 8,
        "T1_us":           200,  "T2_us":   300,
        "jj_width_um":     0.30, "jj_length_um": 0.35,
        "jj_area_um2":     0.105,
        "AlOx_pressure_mbar": 1.0, "AlOx_time_min": 10,
    },
    "XMON_BSM": {
        "cross_width_um":  18,  "cross_length_um": 180, "cross_gap_um": 18,
        "freq_GHz":        5.25, "anharmonicity_MHz": -210,
        "EJ_GHz":          14.0, "EC_MHz": 210, "EJ_EC": 67,
        "Ic_nA":           46,   "Rn_kOhm": 8.7,
        "T1_us":           100,  "T2_us":   150,
        "jj_width_um":     0.28, "jj_length_um": 0.35,
        "jj_area_um2":     0.098,
        "AlOx_pressure_mbar": 1.0, "AlOx_time_min": 10,
    },
    "XMON_ENT": {
        "cross_width_um":  15,  "cross_length_um": 150, "cross_gap_um": 15,
        "freq_GHz":        5.75, "anharmonicity_MHz": -230,
        "EJ_GHz":          11.5, "EC_MHz": 230, "EJ_EC": 50,
        "Ic_nA":           38,   "Rn_kOhm": 10.5,
        "T1_us":           50,   "T2_us":   80,
        "jj_width_um":     0.25, "jj_length_um": 0.30,
        "jj_area_um2":     0.075,
        "AlOx_pressure_mbar": 1.2, "AlOx_time_min": 12,
    },
    "XMON_TC": {
        "cross_width_um":  10,  "cross_length_um": 80, "cross_gap_um": 10,
        "freq_GHz":        7.0,  "anharmonicity_MHz": -300,
        "EJ_GHz":          24.4, "EC_MHz": 300, "EJ_EC": 81,
        "Ic_nA":           80,   "Rn_kOhm": 4.0,
        "T1_us":           20,   "T2_us":   30,
        "jj_width_um":     0.40, "jj_length_um": 0.40,
        "jj_area_um2":     0.160,
        "AlOx_pressure_mbar": 0.5, "AlOx_time_min": 8,
    },
}

# ══════════════════════════════════════════
#  QUANTUM REPEATER PROTOCOL
# ══════════════════════════════════════════

PROTOCOL = """
QUANTUM REPEATER PROTOCOL (Barrett-Kok / DLCZ hybrid):

Step 1 — Entanglement Generation (each node independently):
  • Entanglement qubits (XMON_ENT) interact with microwave-optical transducer
  • Transducer converts microwave photon ↔ telecom photon (1550 nm)
  • Photon sent through optical fibre to neighbouring node
  • Success probability P_ent ≈ 0.01–0.1 per attempt
  • Attempt rate: 1 / (2 × fibre_delay + T_gate) ≈ 1 MHz

Step 2 — Entanglement Storage:
  • Successful entanglement transferred to memory qubits (XMON_MEM)
  • via SWAP gate: T_swap ≈ 50 ns (tunable coupler, g/2π = 10 MHz)
  • Memory coherence time T1 > 200 µs enables 200+ attempts before decay

Step 3 — Bell-State Measurement (relay node only):
  • BSM qubits (XMON_BSM) perform joint Bell measurement
  • Tunable couplers enable CZ gate: T_CZ ≈ 100 ns
  • BSM outcome teleported via classical channel → entanglement swapping
  • Two-qubit gate fidelity target: > 99.5%

Step 4 — Entanglement Purification (optional):
  • 2 noisy EPR pairs → 1 high-fidelity pair via BBPSSW protocol
  • Requires 2 memory + 1 BSM qubit per purification round
  • Threshold fidelity: F_input > 0.5

Performance Targets:
  • End-to-end entanglement rate:  > 100 Hz (for 100 km fibre)
  • End-to-end fidelity:           > 0.90
  • Memory lifetime (T1 × P_ent):  > 200 µs × 0.01 = 2 µs margin
  • Classical communication time:  < 1 ms (for 100 km)
"""

# ══════════════════════════════════════════
#  GDS LAYER MAP
# ══════════════════════════════════════════

LAYER_MAP = {
    1:  ("BASE",        "Nb ground plane",         "negative", "200 nm Nb, DC sputter"),
    2:  ("QUBIT",       "Qubit island",             "positive", "150 nm Al or Nb"),
    3:  ("JJ_BOT",      "JJ bottom electrode",      "positive", "100 nm Al, +17° shadow"),
    4:  ("JJ_BAR",      "JJ tunnel barrier (AlOx)", "positive", "~1.5 nm, in-situ O₂"),
    5:  ("JJ_TOP",      "JJ top electrode/SQUID",   "positive", "120 nm NbTiN, −17° shadow"),
    6:  ("CPW_CON",     "CPW conductor",            "positive", "200 nm Nb, patterned"),
    7:  ("CPW_GAP",     "CPW gap (negative)",       "negative", "Etched Nb"),
    8:  ("FLUX",        "Flux bias line",           "positive", "200 nm Nb or Al"),
    9:  ("AB_PIER",     "Airbridge pier",           "positive", "200 nm NbTiN, sputter"),
    10: ("AB_DECK",     "Airbridge deck",           "positive", "300 nm NbTiN, freestanding"),
    11: ("TRANSDUCER",  "Transducer pad",           "annotation","microwave-optical interface"),
    12: ("NODE_BOUND",  "Node boundary",            "annotation","design reference only"),
    99: ("NO_CHEESE",   "No-cheese KOZ",            "annotation","prevents cheese vias near qubits"),
    100:("CHEESE",      "Cheese via array",         "annotation","flux-trap suppression, r=25µm"),
}

# ══════════════════════════════════════════
#  CELL HIERARCHY
# ══════════════════════════════════════════

CELL_HIERARCHY = """
TOP
├── GROUND_PLANE          (full chip Nb film, negative mask)
├── CHIP_BOUNDARY         (annotation)
├── NODE_0  (Alice)
│   ├── XMON_MEM × 8      (memory qubits)
│   ├── XMON_BSM × 8      (BSM qubits)
│   ├── XMON_ENT × 4      (entanglement qubits)
│   ├── XMON_TC  × 4      (tunable couplers)
│   ├── JJ_QUBIT × 20     (JJ for memory+BSM+ent)
│   ├── JJ_COUPLER × 4    (JJ for tunable couplers)
│   ├── RESONATOR × 12    (λ/4 readout resonators)
│   ├── CLAW_CONN × 24    (coupling claws)
│   ├── FLUX_LINE × 24    (flux bias hairpins)
│   ├── AIRBRIDGE × ~19   (CPW crossovers)
│   ├── TRANSDUCER_PAD × 4
│   └── WIREBOND_PAD × 6
├── NODE_1  (Relay)       [identical structure]
├── NODE_2  (Bob)         [identical structure]
├── AIRBRIDGE × ~6        (inter-node CPW bridges)
└── WIREBOND_PAD × 24     (perimeter I/O)
    [+ 7200 CHEESE polygons inline]
"""

if __name__ == '__main__':
    print("QR72 Architecture Specification")
    print("="*50)
    for k,v in CHIP.items():
        print(f"  {k:25s}: {v}")
    print()
    print(CELL_HIERARCHY)
    print()
    print("Layer Map:")
    for lyr,(name,desc,pol,proc) in LAYER_MAP.items():
        print(f"  {lyr:3d}  {name:12s}  {desc:35s}  [{pol}]")
    print()
    print(PROTOCOL)
