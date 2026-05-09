# ============================================================
# PDK: 24nm Cryo-CMOS Superconducting Qubit Process
# Standard Cell / Primitive Library (primitives.py)
# ============================================================
# Each primitive defines:
#   - Layer usage
#   - Minimum bounding box
#   - Ports (name, layer, position relative to origin)
#   - Key design parameters
# ============================================================

PRIMITIVES = {

    # ==========================================================
    # TRANSMON QUBIT (Cross-shaped capacitor pad + SQUID/JJ)
    # ==========================================================
    "TRANSMON_XMON": {
        "description": "X-mon style transmon qubit. Cross-shaped capacitor pad with SQUID.",
        "layers_used": ["QUBIT_CAP", "JJ_BASE", "JJ_TUNNEL", "JJ_TOP", "JJ_SHUNT", "BASE_METAL"],
        "bbox_um": (500, 500),
        "ports": {
            "COUPLER_N": {"layer": "QUBIT_CAP", "position": (250, 500), "type": "coupling"},
            "COUPLER_S": {"layer": "QUBIT_CAP", "position": (250,   0), "type": "coupling"},
            "COUPLER_E": {"layer": "QUBIT_CAP", "position": (500, 250), "type": "coupling"},
            "COUPLER_W": {"layer": "QUBIT_CAP", "position": (  0, 250), "type": "coupling"},
            "READOUT":   {"layer": "RESONATOR",  "position": (250, 500), "type": "readout"},
            "FLUX_BIAS": {"layer": "CAB",        "position": (250,   0), "type": "flux"},
        },
        "parameters": {
            "cap_arm_width_um": 50,
            "cap_arm_length_um": 150,
            "JJ_area_um2": 0.10,
            "SQUID_loop_um2": 16.0,
            "qubit_freq_GHz": 5.0,
            "anharmonicity_MHz": -200,
            "T1_target_us": 100,
        },
        "notes": "X-mon layout. Requires ground plane opening (BASE_METAL NOT region) around cap arms."
    },

    # ==========================================================
    # TRANSMON QUBIT (Rectangular pad, simpler layout)
    # ==========================================================
    "TRANSMON_RECT": {
        "description": "Rectangular-pad transmon. Two large pads connected by single JJ.",
        "layers_used": ["QUBIT_CAP", "JJ_BASE", "JJ_TUNNEL", "JJ_TOP", "BASE_METAL"],
        "bbox_um": (600, 250),
        "ports": {
            "PAD_A":  {"layer": "QUBIT_CAP", "position": (150, 125), "type": "island"},
            "PAD_B":  {"layer": "QUBIT_CAP", "position": (450, 125), "type": "ground"},
            "READOUT":{"layer": "RESONATOR",  "position": (150,   0), "type": "readout"},
        },
        "parameters": {
            "pad_width_um": 250,
            "pad_length_um": 100,
            "pad_spacing_um": 100,
            "JJ_area_um2": 0.10,
            "qubit_freq_GHz": 5.0,
        },
        "notes": "Simpler DRC compliance. Single JJ (not SQUID) — not flux tunable."
    },

    # ==========================================================
    # FIXED-FREQUENCY TRANSMON (for quantum repeater memory)
    # ==========================================================
    "TRANSMON_MEMORY": {
        "description": "Memory qubit for quantum repeater node. Long T1 optimized.",
        "layers_used": ["QUBIT_CAP", "JJ_BASE", "JJ_TUNNEL", "JJ_TOP", "BASE_METAL"],
        "bbox_um": (700, 300),
        "ports": {
            "READOUT": {"layer": "RESONATOR", "position": (350,   0), "type": "readout"},
            "BUS_IN":  {"layer": "CPW",       "position": (  0, 150), "type": "bus"},
            "BUS_OUT": {"layer": "CPW",       "position": (700, 150), "type": "bus"},
        },
        "parameters": {
            "qubit_freq_GHz": 4.5,
            "JJ_area_um2": 0.12,   # Slightly larger for lower freq
            "T1_target_us": 200,   # Higher T1 priority for memory
            "T2_target_us": 300,
            "pad_width_um": 300,
        },
        "notes": "No SQUID (fixed frequency). Optimized substrate contact geometry for low TLS loss."
    },

    # ==========================================================
    # BSM QUBIT (Bell-State Measurement node)
    # ==========================================================
    "TRANSMON_BSM": {
        "description": "BSM qubit for entanglement swapping in quantum repeater.",
        "layers_used": ["QUBIT_CAP", "JJ_BASE", "JJ_TUNNEL", "JJ_TOP", "JJ_SHUNT", "BASE_METAL"],
        "bbox_um": (500, 500),
        "ports": {
            "READOUT":    {"layer": "RESONATOR", "position": (250,   0), "type": "readout"},
            "LINK_A_IN":  {"layer": "CPW",       "position": (  0, 250), "type": "entanglement_link"},
            "LINK_B_IN":  {"layer": "CPW",       "position": (500, 250), "type": "entanglement_link"},
            "FLUX_BIAS":  {"layer": "CAB",       "position": (250, 500), "type": "flux"},
        },
        "parameters": {
            "qubit_freq_GHz": 5.5,
            "JJ_area_um2": 0.08,   # Higher freq for BSM
            "SQUID_loop_um2": 12.0,
            "T1_target_us": 50,    # Lower T1 OK; speed critical for BSM
            "gate_time_ns": 50,    # Target CZ gate time
        },
        "notes": "Tunable via SQUID for active BSM. BSM requires 2 photon absorption; qubit must be flux-tunable."
    },

    # ==========================================================
    # QUARTER-WAVE READOUT RESONATOR (CPW lambda/4)
    # ==========================================================
    "RESONATOR_QW": {
        "description": "Quarter-wave CPW readout resonator, coupled to qubit and feedline.",
        "layers_used": ["RESONATOR", "BASE_METAL", "CPW"],
        "bbox_um": (4900, 150),
        "ports": {
            "QUBIT_COUPLER": {"layer": "RESONATOR", "position": (   0, 75), "type": "coupling_gap"},
            "FEEDLINE":      {"layer": "CPW",       "position": (4900, 75), "type": "feedline_coupler"},
        },
        "parameters": {
            "freq_GHz": 7.0,
            "conductor_width_um": 10,
            "gap_width_um": 6,
            "length_um": 4800,      # lambda/4 at 7 GHz (v_ph ~ 1.34e8 m/s in Nb CPW on Si)
            "Q_loaded": 5000,
            "kappa_ext_MHz": 1.0,
            "kappa_int_MHz": 0.01,
            "coupling_gap_to_qubit_um": 10,
            "coupling_gap_to_feedline_um": 5,
        },
        "notes": "Meander to fit in bounding box. Meander bend radius >= 50 um. Check AB alignment at each CPW crossing."
    },

    # ==========================================================
    # PURCELL FILTER
    # ==========================================================
    "PURCELL_FILTER": {
        "description": "Purcell filter: bandstop at qubit frequency on readout chain.",
        "layers_used": ["PURCELL", "CPW", "BASE_METAL"],
        "bbox_um": (2000, 200),
        "ports": {
            "IN":  {"layer": "CPW", "position": (   0, 100), "type": "rf_input"},
            "OUT": {"layer": "CPW", "position": (2000, 100), "type": "rf_output"},
        },
        "parameters": {
            "freq_stop_GHz": 5.0,    # Qubit frequency (notch)
            "freq_pass_GHz": 7.0,    # Readout resonator frequency
            "filter_bandwidth_MHz": 100,
            "rejection_dB": 20,
        },
        "notes": "Bandstop filter prevents Purcell decay of qubit via readout line."
    },

    # ==========================================================
    # TUNABLE COUPLER (SQUID-based)
    # ==========================================================
    "TUNABLE_COUPLER": {
        "description": "Flux-tunable transmon coupler between two qubits.",
        "layers_used": ["COUPLER", "JJ_BASE", "JJ_TUNNEL", "JJ_TOP", "CAB", "BASE_METAL"],
        "bbox_um": (400, 300),
        "ports": {
            "QUBIT_A":  {"layer": "COUPLER", "position": (  0, 150), "type": "coupling"},
            "QUBIT_B":  {"layer": "COUPLER", "position": (400, 150), "type": "coupling"},
            "FLUX_BIAS":{"layer": "CAB",     "position": (200,   0), "type": "flux"},
        },
        "parameters": {
            "coupler_freq_GHz": 7.0,    # Off-resonant with qubits
            "SQUID_loop_um2": 10,
            "coupling_strength_MHz": 30, # g_eff when on
            "on_off_ratio": 100,
            "flux_line_mutual_pH": 2.0,  # Mutual inductance to SQUID
        },
        "notes": "CZ gate fidelity >99% target. Flux line must not radiate; add ground shielding vias."
    },

    # ==========================================================
    # AIRBRIDGE CROSSOVER
    # ==========================================================
    "AIRBRIDGE_CROSSOVER": {
        "description": "NbTiN airbridge for CPW crossovers, suppresses slot modes.",
        "layers_used": ["AIRBRIDGE_PIER", "AIRBRIDGE_DECK", "BASE_METAL"],
        "bbox_um": (80, 60),
        "ports": {
            "L_GROUND": {"layer": "AIRBRIDGE_PIER", "position": ( 0, 30), "type": "ground"},
            "R_GROUND": {"layer": "AIRBRIDGE_PIER", "position": (80, 30), "type": "ground"},
        },
        "parameters": {
            "deck_width_um": 10,
            "deck_span_um": 40,
            "pier_footprint_um": 12,
            "bridge_height_um": 3,
            "inductance_pH": 50,
        },
        "notes": "Place every 200um along CPW to prevent parasitic slot-mode resonances."
    },

    # ==========================================================
    # CPW TRANSMISSION LINE SEGMENT
    # ==========================================================
    "CPW_SEGMENT": {
        "description": "Coplanar waveguide segment, 50 Ohm on Si substrate.",
        "layers_used": ["CPW", "BASE_METAL"],
        "bbox_um": (None, 44),   # Length is variable
        "ports": {
            "IN":  {"layer": "CPW", "position": (   0, 22), "type": "rf"},
            "OUT": {"layer": "CPW", "position": (None, 22), "type": "rf"},
        },
        "parameters": {
            "conductor_width_um": 10,
            "gap_width_um": 6,
            "impedance_ohm": 50,
            "velocity_factor": 0.447,   # v/c in Nb on Si at 6GHz
            "attenuation_dB_mm": 0.01,
        },
        "notes": "Conductor width 10 um, gap 6 um gives Z0~50 Ohm for Nb on Si. Verify with EM sim."
    },

    # ==========================================================
    # WIRE BOND PAD
    # ==========================================================
    "WIREBOND_PAD": {
        "description": "Al wire bond pad for package I/O.",
        "layers_used": ["WBP", "CPW"],
        "bbox_um": (100, 150),
        "ports": {
            "CPW_IN": {"layer": "CPW", "position": ( 50,   0), "type": "rf"},
            "BOND":   {"layer": "WBP", "position": ( 50, 125), "type": "wire_bond"},
        },
        "parameters": {
            "pad_width_um": 80,
            "pad_length_um": 120,
            "taper_length_um": 100,
            "taper_start_width_um": 10,
        },
        "notes": "CPW-to-pad taper required. Inductance: ~1 nH/mm wire. Max wire length 5mm."
    },

    # ==========================================================
    # INDIUM FLIP-CHIP BUMP BOND
    # ==========================================================
    "FLIPCHIP_BUMP": {
        "description": "Indium pillar bump for flip-chip integration.",
        "layers_used": ["INPILLAR_FLIP", "INPILLAR_BASE", "TINPAD_FLIP", "TINPAD_BASE"],
        "bbox_um": (50, 50),
        "ports": {
            "FLIP_PAD": {"layer": "TINPAD_FLIP", "position": (25, 25), "type": "bump_top"},
            "BASE_PAD": {"layer": "TINPAD_BASE", "position": (25, 25), "type": "bump_bot"},
        },
        "parameters": {
            "pillar_diameter_um": 12,
            "pillar_height_um": 8,
            "tinpad_size_um": 25,
            "tinpad_enc_um": 5,
            "pitch_um": 50,
            "contact_resistance_mohm": 5,
            "parasitic_cap_fF": 10,
        },
        "notes": "In-In thermocompression bonding. TiN surface prep required. Check BBox enclosure DRC."
    },

    # ==========================================================
    # CRYO-CMOS UNIT CELL (24nm node, 4K operation)
    # ==========================================================
    "CMOS_READOUT_CELL": {
        "description": "Single qubit readout amplifier cell (NMOS-only, 4K rated).",
        "layers_used": ["GATE", "M0", "M1", "M2", "CONT", "VIA1"],
        "bbox_um": (5, 5),
        "ports": {
            "VDD":   {"layer": "M1", "position": (2.5, 5),   "type": "power"},
            "VSS":   {"layer": "M1", "position": (2.5, 0),   "type": "ground"},
            "IN":    {"layer": "M0", "position": (  0, 2.5), "type": "signal"},
            "OUT":   {"layer": "M0", "position": (  5, 2.5), "type": "signal"},
            "BIAS":  {"layer": "M1", "position": (2.5, 2.5), "type": "bias"},
        },
        "parameters": {
            "transistor_W_nm": 960,    # Multi-finger (40 x 24nm gate)
            "transistor_L_nm": 24,
            "fingers": 40,
            "VDD_V": 0.9,              # 4K nominal supply
            "noise_figure_dB": 1.0,
            "gain_dB": 20,
            "bandwidth_GHz": 8,
            "power_mW": 0.1,
        },
        "notes": "NMOS only. PMOS not reliable at 4K in 24nm bulk. Guard rings required."
    },

    # ==========================================================
    # FLUX BIAS LINE (DC, for SQUID tuning)
    # ==========================================================
    "FLUX_BIAS_LINE": {
        "description": "DC current line for flux tuning of SQUID-based elements.",
        "layers_used": ["CAB", "BASE_METAL"],
        "bbox_um": (None, 20),
        "ports": {
            "DC_IN":  {"layer": "CAB", "position": (   0, 10), "type": "dc"},
            "DC_OUT": {"layer": "CAB", "position": (None, 10), "type": "dc"},
        },
        "parameters": {
            "line_width_um": 5,
            "line_to_SQUID_spacing_um": 10,
            "mutual_inductance_to_SQUID_pH": 2.0,
            "max_current_mA": 2.0,
            "flux_per_mA_Phi0": 0.5,    # Phi0/mA coupling efficiency
        },
        "notes": "Must be shielded from qubit E-field. Ground plane slots around bias line forbidden."
    },

    # ==========================================================
    # MICROWAVE-OPTICAL TRANSDUCER STUB
    # ==========================================================
    "TRANSDUCER_PAD": {
        "description": "Interface pad for electro-optic or piezoelectric microwave-to-optical transducer.",
        "layers_used": ["RESONATOR", "CPW", "BASE_METAL"],
        "bbox_um": (500, 500),
        "ports": {
            "MICROWAVE_IN": {"layer": "CPW",      "position": (250,   0), "type": "rf"},
            "OPTICAL_PORT": {"layer": "BASE_METAL","position": (250, 500), "type": "optical_waveguide"},
        },
        "parameters": {
            "microwave_freq_GHz": 5.0,
            "optical_wavelength_nm": 1550,
            "transducer_type": "electro-optic (LiNbO3 or AlN piezo)",
            "coupling_rate_MHz": 1.0,
            "internal_loss_rate_MHz": 0.1,
        },
        "notes": (
            "For quantum repeater: converts qubit state to 1550nm photon. "
            "KOZ_CRYO must be > 1000 um. Bond wire from CMOS control separately."
        )
    },
}

# ============================================================
# DEVICE NAMING CONVENTION
# ============================================================
NAMING_CONVENTION = """
Device instance names follow the pattern:
  <CELL_TYPE>_<QUBIT_INDEX>_<INSTANCE>

Examples:
  TRANSMON_MEMORY_Q0_I0    -> Memory qubit 0
  TRANSMON_BSM_Q1_I0       -> BSM qubit 1
  RESONATOR_QW_Q0_R0       -> Readout resonator for qubit 0
  AIRBRIDGE_CROSSOVER_AB12 -> Airbridge instance 12
  FLIPCHIP_BUMP_FC04       -> Flip-chip bump 4

Net names:
  CPW_BUS_<N>              -> Microwave bus N
  FLUX_Q<N>               -> Flux bias line for qubit N
  READOUT_<N>             -> Readout feedline N
  ENTANGLE_LINK_<A>_<B>   -> Entanglement link between nodes A and B
"""
