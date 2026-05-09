"""
scripts/generate_gds.py
GDS Export Script — Quantum Repeater PDK
Generates all primitive cells, top-level assembly, and exports to GDS/OASIS
"""

from __future__ import annotations
import os, sys, json, argparse
from pathlib import Path
from dataclasses import asdict

# Add PDK root to path
PDK_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PDK_ROOT))

try:
    import gdsfactory as gf
    GF_AVAILABLE = True
except ImportError:
    GF_AVAILABLE = False
    print("WARNING: gdsfactory not installed. Install with: pip install gdsfactory")


def export_primitives(output_dir: Path) -> dict:
    """Export all primitive cells to individual GDS files."""
    from primitives.josephson_junction import DolanJJ, DCSQUID, ManhattanJJ
    from primitives.transmon_qubit import TransmonQubit, TunableTransmon, XmonQubit
    from primitives.cpw_resonator import CPWResonator, PurcellFilter

    exported = {}

    primitives = [
        # (cell_object, filename)
        (DolanJJ(width_nm=300, height_nm=300),
         "jj_dolan_300nm.gds"),

        (DolanJJ(width_nm=500, height_nm=500),
         "jj_dolan_500nm.gds"),

        (ManhattanJJ(width_nm=400, overlap_nm=350),
         "jj_manhattan_350nm.gds"),

        (DCSQUID(loop_width_um=4.0, loop_height_um=2.0),
         "squid_4x2um.gds"),

        (TransmonQubit(qubit_freq_GHz=5.0),
         "transmon_5GHz.gds"),

        (TransmonQubit(qubit_freq_GHz=5.5),
         "transmon_5p5GHz.gds"),

        (TunableTransmon(max_freq_GHz=5.5, min_freq_GHz=4.0),
         "transmon_tunable_4to5p5GHz.gds"),

        (XmonQubit(qubit_freq_GHz=5.0),
         "xmon_5GHz.gds"),

        (CPWResonator(frequency_GHz=6.5, mode="quarter"),
         "cpw_resonator_6p5GHz_quarter.gds"),

        (CPWResonator(frequency_GHz=6.8, mode="quarter"),
         "cpw_resonator_6p8GHz_quarter.gds"),

        (CPWResonator(frequency_GHz=5.5, mode="half"),
         "cpw_resonator_5p5GHz_half.gds"),

        (PurcellFilter(readout_freq_GHz=6.8, qubit_freq_GHz=5.0),
         "purcell_filter_6p8GHz.gds"),
    ]

    for prim, fname in primitives:
        fpath = output_dir / "primitives" / fname
        fpath.parent.mkdir(parents=True, exist_ok=True)
        try:
            if GF_AVAILABLE:
                cell = prim.build()
                cell.write_gds(str(fpath))
                print(f"  ✓ {fname}")
            exported[fname] = str(fpath)
        except Exception as e:
            print(f"  ✗ {fname}: {e}")

    return exported


def export_repeater_node(
    n_qubits: int = 4,
    qubit_freqs: list = None,
    readout_freqs: list = None,
    output_dir: Path = None,
    format: str = "gds",
) -> Path:
    """Export the full repeater node layout."""
    from cells.repeater_node import RepeaterNode

    if qubit_freqs is None:
        qubit_freqs = [4.8, 5.1, 5.4, 5.7][:n_qubits]
    if readout_freqs is None:
        readout_freqs = [6.5, 6.7, 6.9, 7.1][:n_qubits]
    if output_dir is None:
        output_dir = PDK_ROOT / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nBuilding RepeaterNode ({n_qubits} qubits)...")
    node = RepeaterNode(
        n_qubits=n_qubits,
        process="Al_Si_150nm",
        qubit_freq_GHz=qubit_freqs,
        readout_freq_GHz=readout_freqs,
        g_MHz=[80.0] * n_qubits,
        qubit_types=["fixed" if i % 2 == 0 else "tunable" for i in range(n_qubits)],
        include_memory=True,
        include_bsm=True,
    )

    # Save design report
    report = node.generate_report()
    report_path = output_dir / "repeater_node_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"  ✓ Design report: {report_path}")

    # Build and export GDS
    out_path = None
    if GF_AVAILABLE:
        try:
            chip = node.build()
            fname = f"repeater_node_{n_qubits}q.{format}"
            out_path = output_dir / fname
            if format == "gds":
                chip.write_gds(str(out_path))
            elif format == "oas":
                chip.write_oas(str(out_path))
            print(f"  ✓ Layout: {out_path}")
        except Exception as e:
            print(f"  ✗ Layout export failed: {e}")

    return out_path


def run_pdk_validation() -> bool:
    """Basic PDK integrity check."""
    print("\n=== PDK Validation ===")
    errors = []

    # Check required files
    required_files = [
        "pdk_config.yaml",
        "tech/process_stack.yaml",
        "tech/material_properties.yaml",
        "design_rules/drc_rules.yaml",
        "design_rules/drc_klayout.lydrc",
        "primitives/josephson_junction.py",
        "primitives/transmon_qubit.py",
        "primitives/cpw_resonator.py",
        "cells/repeater_node.py",
        "models/spice/transmon.cir",
        "models/hamiltonian/transmon_ham.py",
        "simulations/sim_config.yaml",
    ]

    for f in required_files:
        fpath = PDK_ROOT / f
        if fpath.exists():
            print(f"  ✓ {f}")
        else:
            print(f"  ✗ MISSING: {f}")
            errors.append(f)

    # Check Python imports
    try:
        from primitives.josephson_junction import DolanJJ
        jj = DolanJJ(width_nm=300, height_nm=300)
        spec = jj.spec_summary()
        assert spec["area_um2"] > 0
        print(f"  ✓ DolanJJ: Ic={spec['Ic_nA']}nA, EJ={spec['EJ_GHz']}GHz")
    except Exception as e:
        errors.append(f"DolanJJ: {e}")

    try:
        from primitives.transmon_qubit import TransmonQubit
        t = TransmonQubit(qubit_freq_GHz=5.0)
        info = t.qubit_info
        assert 4.0 < info["f_01_GHz"] < 6.0
        print(f"  ✓ Transmon: f={info['f_01_GHz']}GHz, EC={info['EC_MHz']}MHz")
    except Exception as e:
        errors.append(f"Transmon: {e}")

    try:
        from primitives.cpw_resonator import CPWResonator
        r = CPWResonator(frequency_GHz=6.8)
        s = r.resonator_summary()
        assert s["resonator_length_um"] > 0
        print(f"  ✓ CPWResonator: L={s['resonator_length_um']}µm")
    except Exception as e:
        errors.append(f"CPWResonator: {e}")

    try:
        from models.hamiltonian.transmon_ham import TransmonHamiltonian
        th = TransmonHamiltonian(EC_MHz=250, EJ_GHz=15.0)
        sm = th.summary()
        print(f"  ✓ TransmonHam: f01={sm['f_01_GHz']}GHz, α={sm['anharmonicity_MHz']}MHz")
    except Exception as e:
        errors.append(f"TransmonHam: {e}")

    print(f"\nValidation: {len(errors)} error(s)")
    return len(errors) == 0


def main():
    parser = argparse.ArgumentParser(description="Quantum Repeater PDK — GDS Generator")
    parser.add_argument("--output",   default="output",  help="Output directory")
    parser.add_argument("--n-qubits", type=int, default=4, help="Number of qubits")
    parser.add_argument("--validate", action="store_true", help="Run PDK validation")
    parser.add_argument("--primitives", action="store_true", help="Export all primitives")
    parser.add_argument("--format", default="gds", choices=["gds", "oas"],
                        help="Output format")
    args = parser.parse_args()

    output_dir = PDK_ROOT / args.output

    if args.validate:
        ok = run_pdk_validation()
        sys.exit(0 if ok else 1)

    if args.primitives:
        print("\nExporting primitive cells...")
        export_primitives(output_dir)

    print("\nExporting repeater node...")
    export_repeater_node(
        n_qubits=args.n_qubits,
        output_dir=output_dir,
        format=args.format,
    )
    print("\nDone.")


if __name__ == "__main__":
    main()
