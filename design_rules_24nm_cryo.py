# ============================================================
# PDK: 24nm Cryo-CMOS Superconducting Qubit Process
# Design Rule Specification (design_rules.py)
# Target: Quantum Repeater Measurement Chip
# Operating temperature: 10-20 mK (qubit plane), 4K (cryo-CMOS)
# ============================================================

# ============================================================
# SECTION 1: CRYO-CMOS PHYSICAL DESIGN RULES (24nm node, 4K)
# ============================================================

CRYO_CMOS_RULES = {
    # Gate rules
    "GW1_gate_min_width_um":          0.024,   # Effective gate length, 24nm node
    "GW2_gate_max_width_um":          10.0,    # Max gate width (multi-finger)
    "GS1_gate_min_spacing_um":        0.048,   # Gate-to-gate spacing
    "GS2_gate_to_active_enc_um":      0.010,   # Gate enclosure of active

    # Metal 1 rules (Al, 200nm thick)
    "M1W1_min_width_um":              0.050,
    "M1W2_max_width_um":              5.0,
    "M1S1_min_spacing_um":            0.060,
    "M1A1_min_area_um2":              0.005,

    # Metal 2 rules (Al, 350nm thick)
    "M2W1_min_width_um":              0.080,
    "M2S1_min_spacing_um":            0.100,
    "M2A1_min_area_um2":              0.010,

    # Via rules
    "V1_min_size_um":                 0.030,
    "V1_enc_by_M1_um":                0.010,
    "V1_enc_by_M2_um":                0.010,
    "V1_spacing_um":                  0.040,
    "V2_min_size_um":                 0.040,
    "V2_enc_by_M2_um":                0.015,
    "V2_spacing_um":                  0.060,

    # Cryogenic derating (low-T carrier freeze-out effects)
    # At 4K: use n-type MOSFET only (p-type freeze out risk)
    "cryo_min_VDD_V":                 0.6,     # Min supply for 4K operation
    "cryo_max_VDD_V":                 1.2,     # Max supply at 4K
    "cryo_preferred_device":          "NMOS",  # PMOS unreliable at 4K in 24nm bulk

    # ESD / Latchup (supressed at 4K, but guard rings still required)
    "latchup_guard_ring_spacing_um":  2.0,
}

# ============================================================
# SECTION 2: JOSEPHSON JUNCTION RULES
# ============================================================

JJ_RULES = {
    # Dimensions (shadow-evaporation double-angle technique)
    "JJ1_min_area_um2":               0.04,    # Sets Ej; min for reliable oxidation
    "JJ2_max_area_um2":               0.25,    # Max area; above this Ej/Ec ratio too large
    "JJ3_target_area_um2":            0.10,    # Target for 5 GHz transmon
    "JJ4_min_spacing_um":             2.0,     # JJ-to-JJ isolation
    "JJ5_base_enc_um":                0.2,     # Bottom electrode enclosure of tunnel junction
    "JJ6_top_enc_um":                 0.2,     # Top electrode enclosure of tunnel junction
    "JJ7_to_metal1_spacing_um":       1.0,     # JJ to CMOS metal isolation
    "JJ8_to_KOZ_spacing_um":          5.0,     # JJ proximity exclusion zone
    "JJ9_shunt_enc_um":               3.0,     # Shunt cap enclosure of JJ

    # Electrical targets
    "JJ_Jc_nominal_uA_um2":          0.5,     # Critical current density (uA/um²)
    "JJ_EJ_target_GHz":              15.0,     # Josephson energy (in frequency units)
    "JJ_EC_target_MHz":             200.0,     # Charging energy (EC = e²/2C)
    "JJ_EJ_EC_ratio_target":         75.0,     # EJ/EC for transmon regime (>>1)
    "JJ_anharmonicity_target_MHz": -200.0,     # Desired anharmonicity

    # SQUID (Superconducting Quantum Interference Device) rules
    "SQUID_loop_area_um2_min":        4.0,     # Min loop area
    "SQUID_loop_area_um2_max":       50.0,     # Max loop; controls flux sensitivity
    "SQUID_junction_ratio_min":       0.5,     # Ratio Jc1/Jc2 min (asymmetry)
    "SQUID_junction_ratio_max":       2.0,     # Ratio Jc1/Jc2 max
}

# ============================================================
# SECTION 3: QUBIT DESIGN RULES
# ============================================================

QUBIT_RULES = {
    # Transmon qubit capacitor pad
    "QC1_pad_min_width_um":          50.0,
    "QC2_pad_min_length_um":        100.0,
    "QC3_pad_to_pad_spacing_um":     80.0,    # Between the two pads of one transmon
    "QC4_qubit_to_qubit_spacing_um":200.0,    # Between adjacent transmons (ZZ isolation)
    "QC5_qubit_to_ground_spacing_um":20.0,    # Pad to ground plane clearance

    # Coupling to readout resonator
    "QC6_coupling_gap_min_um":        3.0,
    "QC6_coupling_gap_max_um":       30.0,
    "QC6_coupling_gap_target_um":    10.0,    # ~50 MHz coupling strength

    # Coupling to tunable coupler
    "QC7_coupler_gap_min_um":         5.0,
    "QC7_coupler_gap_target_um":     15.0,

    # Electrical targets
    "qubit_freq_target_GHz":          5.0,    # Target qubit transition freq
    "qubit_freq_spread_MHz":         50.0,    # Max allowed freq spread across die
    "qubit_T1_target_us":           100.0,    # Target T1 coherence time
    "qubit_T2_target_us":           150.0,    # Target T2* (Ramsey)
    "qubit_anharmonicity_MHz":     -200.0,    # Negative anharmonicity (transmon)

    # Purcell protection
    "purcell_filter_spacing_um":      5.0,    # Purcell filter enclosure
}

# ============================================================
# SECTION 4: RESONATOR DESIGN RULES
# ============================================================

RESONATOR_RULES = {
    "RES1_conductor_min_width_um":    5.0,    # CPW conductor width (resonator section)
    "RES2_gap_min_width_um":          3.0,    # CPW gap width (resonator section)
    "RES3_resonator_spacing_um":     30.0,    # Resonator-to-resonator isolation
    "RES4_to_qubit_cap_gap_min_um":   3.0,
    "RES4_to_qubit_cap_gap_max_um":  30.0,
    "RES5_length_quarter_wave_um": 4800.0,   # lambda/4 at 7 GHz in Nb CPW (approx)
    "RES6_freq_target_GHz":           7.0,    # Readout resonator frequency
    "RES7_freq_spread_MHz":          50.0,    # Allowed spread across die
    "RES8_kappa_ext_MHz":             1.0,    # External coupling rate (kappa_ext)
    "RES9_kappa_int_MHz":             0.01,   # Internal loss rate target (high-Q)
    "RES10_Q_loaded_target":        5000,     # Loaded Q target

    # Purcell filter
    "purcell_freq_offset_MHz":      500.0,   # Purcell frequency from qubit
    "purcell_bandwidth_MHz":        100.0,   # Purcell filter bandwidth
}

# ============================================================
# SECTION 5: CPW (COPLANAR WAVEGUIDE) DESIGN RULES
# ============================================================

CPW_RULES = {
    # Geometry (50-ohm targeting for Nb on Si, epsilon_eff ~ 6.5)
    "CPW1_conductor_min_width_um":    2.0,
    "CPW2_conductor_target_width_um": 10.0,   # ~50 Ohm with 6 um gap on Si
    "CPW3_gap_min_um":                3.0,
    "CPW4_gap_target_um":             6.0,
    "CPW5_external_spacing_um":      50.0,    # CPW-to-CPW isolation
    "CPW6_bend_radius_min_um":        50.0,   # Min bend radius (< => radiation loss)
    "CPW7_to_JJ_spacing_um":         10.0,
    "CPW8_to_ground_plane_um":       10.0,    # CPW gap to adjacent ground plane

    # Electrical targets
    "CPW_impedance_ohm":             50.0,    # Target characteristic impedance
    "CPW_impedance_tolerance_ohm":    2.0,    # +/- tolerance
    "CPW_attenuation_dB_per_mm":      0.01,   # At 6 GHz, 4K

    # Crossovers (via airbridges)
    "CPW_AB_spacing_um":             200.0,   # Max spacing between airbridges
                                              # (prevent slot-mode excitation)
    "CPW_AB_min_spacing_um":          20.0,   # Min airbridge-to-airbridge

    # T-junction / splitter rules
    "CPW_junction_overlap_um":         5.0,   # Conductor overlap at T-junction
}

# ============================================================
# SECTION 6: AIRBRIDGE DESIGN RULES
# ============================================================

AIRBRIDGE_RULES = {
    "AB1_pier_to_CPW_spacing_um":     2.0,
    "AB2_pier_deck_enclosure_um":     2.0,    # Deck overlap onto pier
    "AB3_deck_to_deck_spacing_um":   20.0,
    "AB4_deck_min_width_um":          4.0,    # Mechanical + electrical
    "AB5_deck_max_span_um":          60.0,    # Max freestanding span
    "AB6_deck_target_width_um":      10.0,
    "AB7_deck_target_span_um":       40.0,
    "AB8_pier_height_nm":           3000,     # 3 um sacrificial spacer
    "AB9_to_qubit_spacing_um":       10.0,
    "AB10_center_to_CPW_tol_um":      1.0,   # Center alignment tolerance

    # Electrical
    "AB_resistance_target_mohm":      5.0,   # Max contact resistance
    "AB_inductance_pH":              50.0,   # Parasitic inductance (50 pH per bridge)
}

# ============================================================
# SECTION 7: FLIP-CHIP / INDIUM PILLAR RULES
# ============================================================

FLIPCHIP_RULES = {
    "FC1_inpillar_min_diameter_um":   8.0,
    "FC2_inpillar_target_diameter_um":12.0,
    "FC3_inpillar_to_inpillar_um":   15.0,   # Pitch: min spacing
    "FC4_inpillar_target_pitch_um":  50.0,
    "FC5_tinpad_min_area_um2":      100.0,
    "FC6_tinpad_enc_of_inpillar_um":  5.0,   # TiN pad enclosure of In pillar
    "FC7_inpillar_BBox_enc_um":      10.0,   # BBox enclosure check
    "FC8_tinpad_to_AB_um":           50.0,
    "FC9_tinpad_to_CPW_um":          10.0,
    "FC10_flip_gap_um":            5000.0,   # Flip-chip bonding gap (5 um In compression)

    # Electrical
    "FC_contact_resistance_mohm":     5.0,
    "FC_bump_capacitance_fF":        10.0,   # Per bump, parasitic
}

# ============================================================
# SECTION 8: WIRE BOND PAD RULES
# ============================================================

WBP_RULES = {
    "WBP1_pad_min_width_um":         60.0,
    "WBP2_pad_min_length_um":       100.0,
    "WBP3_pad_to_pad_spacing_um":    50.0,
    "WBP4_parallel_edge_spacing_um":300.0,
    "WBP5_to_CPW_spacing_um":       100.0,
    "WBP6_to_qubit_cap_spacing_um": 300.0,
    "WBP7_target_pitch_um":         150.0,

    # Wire bond specs
    "WBP_wire_diameter_um":          25.0,   # Al wire, 25 um
    "WBP_max_wire_length_mm":         5.0,
    "WBP_inductance_nH_per_mm":       1.0,
}

# ============================================================
# SECTION 9: QUANTUM REPEATER SPECIFIC DESIGN RULES
# ============================================================

QUANTUM_REPEATER_RULES = {
    # Node architecture: each node has N memory qubits + BSM qubits
    "QR1_BSM_qubit_isolation_um":    500.0,  # BSM to memory qubit isolation
    "QR2_microwave_optical_KOZ_um": 1000.0,  # Transducer exclusion zone
    "QR3_CPW_matched_length_tol_um": 10.0,   # Electrical length matching
    "QR4_readout_chain_spacing_um":   5.0,   # Readout channel isolation
    "QR5_flux_line_to_JJ_um":        10.0,   # Flux bias to qubit JJ
    "QR6_memory_qubit_freq_GHz":      4.5,   # Memory qubit target
    "QR7_BSM_qubit_freq_GHz":         5.5,   # BSM qubit target
    "QR8_entanglement_swap_fidelity":  0.99, # Target fidelity
    "QR9_node_qubit_count":           10,    # Qubits per repeater node
    "QR10_multiplexing_channels":      4,    # Simultaneous entanglement channels

    # Microwave-optical transducer interface
    "transducer_optical_wavelength_nm": 1550,  # C-band telecom photon
    "transducer_microwave_freq_GHz":    5.0,
    "transducer_coupling_MHz":          1.0,   # Target electro-optic coupling
}

# ============================================================
# SECTION 10: DIE & PACKAGING RULES
# ============================================================

DIE_RULES = {
    "DIE1_min_size_um":            1000.0,
    "DIE2_max_size_um":           10000.0,   # 10mm max for flip-chip stress
    "DIE3_scribe_lane_um":          100.0,
    "DIE4_edge_keepout_um":         200.0,   # No devices within 200um of die edge

    # Substrate
    "substrate_material":           "Si (intrinsic, >10 kOhm·cm)",
    "substrate_thickness_um":       525,
    "substrate_orientation":        "(100)",
    "substrate_resistivity_ohm_cm": ">10000",  # Required for low microwave loss

    # Packaging
    "package_type":                 "Flip-chip on PCB or interposer",
    "chip_temperature_mK":           15,
    "CMOS_temperature_K":             4,
    "dilution_fridge_stage":        "MXC (mixing chamber)",
}

# ============================================================
# SECTION 11: PROCESS PARAMETERS (for simulation use)
# ============================================================

PROCESS_PARAMS = {
    # Superconducting materials
    "Nb_Tc_K":                        9.2,
    "Nb_lambda_L_nm":                 90,     # London penetration depth
    "Nb_ksi_nm":                      38,     # Coherence length
    "Nb_resistivity_uOhm_cm":        14.5,    # Normal state (above Tc)

    "Al_Tc_K":                        1.2,
    "Al_lambda_L_nm":                 50,
    "Al_ksi_nm":                    1600,
    "Al_resistivity_uOhm_cm":         2.65,

    "NbTiN_Tc_K":                    14.0,   # For airbridges
    "NbTiN_lambda_L_nm":             300,
    "NbTiN_sheet_resistance_sq_ohm":  10,    # Normal state

    "TiN_Tc_K":                       4.0,
    "TiN_kinetic_inductance_pH_sq":   20,    # High kinetic inductance

    # Dielectrics
    "SiO2_epsilon_r":                 3.9,
    "Si_epsilon_r":                  11.9,
    "vacuum_gap_epsilon_r":           1.0,

    # JJ tunnel barrier
    "AlOx_barrier_thickness_nm":      1.5,
    "AlOx_Jc_uA_um2":                0.5,    # Critical current density nominal
    "AlOx_uniformity_percent_1sigma": 2.0,   # JJ area uniformity

    # Cryogenic CMOS parameters (24nm bulk, at 4K)
    "NMOS_Vth_mV_4K":               500,     # Threshold shift at 4K
    "NMOS_mobility_cm2_Vs_4K":      700,     # Increased at low T
    "NMOS_noise_V2_Hz":             1e-18,   # Noise spectral density at 4K
    "CMOS_power_mW_per_qubit":        0.1,   # Target CMOS power budget
}
