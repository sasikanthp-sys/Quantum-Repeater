"""
cells/repeater_node.py
Full Quantum Repeater Node — Top-Level Layout Assembly

A quantum repeater node contains:
  1. N data qubits (transmon)          — stores entanglement
  2. N communication qubits (transmon) — interfaces with fiber/microwave link
  3. N readout resonators + Purcell filters
  4. SQUID tunable couplers between qubit pairs
  5. Bell-State Measurement (BSM) circuits
  6. Quantum memory interface bus
  7. Classical control: flux bias lines, drive lines, DC bias
  8. Bond pads and output ports
  9. Ground plane with flux-trapping holes
  10. Air-bridge crossovers

Architecture (4-qubit repeater node example):
  ┌─────────────────────────────────────────────────────┐
  │  PORT_A (fiber/MW link)         PORT_B (fiber/MW)   │
  │      │                               │              │
  │  [BSM_A]                         [BSM_B]            │
  │      │                               │              │
  │  [Q_comm_0] ─── [Coupler_01] ─── [Q_comm_1]        │
  │      │                               │              │
  │  [Q_data_0] ─── [Coupler_01] ─── [Q_data_1]        │
  │      │                               │              │
  │  [RO_0][PF_0]               [RO_1][PF_1]            │
  │                                                     │
  │         QUANTUM MEMORY BUS                          │
  └─────────────────────────────────────────────────────┘
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
import gdsfactory as gf
from gdsfactory import Component

from primitives.transmon_qubit import TransmonQubit, TunableTransmon
from primitives.cpw_resonator import CPWResonator, PurcellFilter
from primitives.josephson_junction import DCSQUID

LAYER_BASE  = (1, 0)
LAYER_AB    = (5, 0)
LAYER_PAD   = (7, 0)
LAYER_HOLES = (10, 0)
LAYER_LABEL = (200, 0)
LAYER_ANNOT = (201, 0)
LAYER_DICE  = (202, 0)

# ── Chip-level constants ──────────────────────────────────────
CHIP_WIDTH_UM  = 7000.0   # 7 mm
CHIP_HEIGHT_UM = 7000.0   # 7 mm
EDGE_KEEPOUT   = 300.0    # µm from chip edge
PAD_SIZE_UM    = 100.0    # bond pad size
PAD_PITCH_UM   = 200.0    # bond pad pitch


@dataclass
class QubitCell:
    """
    Single qubit unit cell: qubit + readout resonator + Purcell filter + bias lines.
    """
    qubit_freq_GHz: float = 5.0
    readout_freq_GHz: float = 6.8
    anharmonicity_MHz: float = -250.0
    g_MHz: float = 80.0
    Qi: float = 1e5
    Qc: float = 3000.0
    qubit_type: str = "fixed"   # "fixed" or "tunable"
    index: int = 0
    name: str = ""

    def __post_init__(self):
        if not self.name:
            self.name = f"QubitCell_{self.index}"

    def build(self) -> Component:
        c = gf.Component(self.name)

        # ── Transmon qubit ────────────────────────────────────
        if self.qubit_type == "fixed":
            q = TransmonQubit(
                qubit_freq_GHz=self.qubit_freq_GHz,
                anharmonicity_MHz=self.anharmonicity_MHz,
                name=f"Q{self.index}",
            ).build()
        else:
            q = TunableTransmon(
                max_freq_GHz=self.qubit_freq_GHz + 0.5,
                min_freq_GHz=self.qubit_freq_GHz - 0.5,
                name=f"TQ{self.index}",
            ).build()
        q_ref = c.add_ref(q)
        q_ref.move((0, 0))

        # ── Purcell filter ─────────────────────────────────────
        pf = PurcellFilter(
            readout_freq_GHz=self.readout_freq_GHz,
            qubit_freq_GHz=self.qubit_freq_GHz,
            bandwidth_MHz=200.0,
            name=f"PF{self.index}",
        ).build()
        pf_ref = c.add_ref(pf)
        pf_ref.move((0, 1100))

        # ── Readout resonator ─────────────────────────────────
        ro = CPWResonator(
            frequency_GHz=self.readout_freq_GHz,
            mode="quarter",
            Qi_target=self.Qi,
            Qc_target=self.Qc,
            name=f"RO{self.index}",
        ).build()
        ro_ref = c.add_ref(ro)
        ro_ref.move((200, 600))

        # ── Flux bias line (for tunable qubit only) ───────────
        if self.qubit_type == "tunable":
            fl = self._make_flux_line()
            fl_ref = c.add_ref(fl)
            fl_ref.move((-200, 500))

        # ── Drive line ────────────────────────────────────────
        dl = self._make_drive_line()
        dl_ref = c.add_ref(dl)
        dl_ref.move((600, 400))

        # Ports
        c.add_port(f"readout_{self.index}",
                   center=(200, 0), width=10, orientation=90, layer=LAYER_BASE)
        c.add_port(f"drive_{self.index}",
                   center=(700, 400), width=10, orientation=0, layer=LAYER_BASE)

        return c

    def _make_flux_line(self) -> Component:
        c = gf.Component(f"FluxLine_{self.index}")
        # Narrow CPW line (5 µm / 3 µm) approaching SQUID
        c.add_ref(gf.components.rectangle(size=(5, 200), layer=LAYER_BASE))
        c.add_port("tip", center=(2.5, 0), width=5, orientation=270,
                   layer=LAYER_BASE)
        c.add_port("bond", center=(2.5, 200), width=5, orientation=90,
                   layer=LAYER_BASE)
        return c

    def _make_drive_line(self) -> Component:
        c = gf.Component(f"DriveLine_{self.index}")
        # Capacitively coupled drive line
        c.add_ref(gf.components.rectangle(size=(10, 100), layer=LAYER_BASE))
        c.add_port("input", center=(5, 100), width=10, orientation=90,
                   layer=LAYER_BASE)
        return c


@dataclass
class BSMCell:
    """
    Bell-State Measurement (BSM) cell for entanglement swapping.

    The BSM consists of:
      - 50/50 beam splitter (CPW directional coupler)
      - Two detector qubits / single-photon detectors
      - Coincidence circuit logic

    For superconducting implementation:
      - Microwave beam splitter via λ/4 hybrid coupler
      - Transmon-based photon detection (dispersive readout)
      - Classical feedback line for heralded entanglement
    """
    freq_GHz: float = 6.0
    coupling_strength: float = 0.5  # 50/50 = 0.5
    name: str = "BSM"

    def build(self) -> Component:
        c = gf.Component(self.name)

        # λ/4 hybrid coupler (90° hybrid)
        # Two parallel CPW lines coupled over λ/4 length
        vp = 299792458 * 1e-3 / math.sqrt(6.45)   # µm/ns
        lam4 = vp / self.freq_GHz / 4  # µm

        line_w = 10.0
        gap    = 6.0
        coup_gap = 4.0   # coupling gap between lines

        # Input CPW 1
        in1 = c.add_ref(
            gf.components.rectangle(size=(lam4, line_w), layer=LAYER_BASE)
        )
        in1.move((0, 0))

        # Input CPW 2 (parallel, offset by line_w + coup_gap)
        in2 = c.add_ref(
            gf.components.rectangle(size=(lam4, line_w), layer=LAYER_BASE)
        )
        in2.move((0, line_w + coup_gap))

        # Through and coupled output labels
        c.add_port("port1_in",  center=(0, line_w / 2),
                   width=line_w, orientation=180, layer=LAYER_BASE)
        c.add_port("port2_in",  center=(0, line_w + coup_gap + line_w / 2),
                   width=line_w, orientation=180, layer=LAYER_BASE)
        c.add_port("port1_out", center=(lam4, line_w / 2),
                   width=line_w, orientation=0, layer=LAYER_BASE)
        c.add_port("port2_out", center=(lam4, line_w + coup_gap + line_w / 2),
                   width=line_w, orientation=0, layer=LAYER_BASE)

        c.add_label(
            text=f"BSM\n{self.freq_GHz}GHz\n50/50 Coupler",
            position=(lam4 / 2, -20),
            layer=LAYER_LABEL,
        )
        return c


@dataclass
class QuantumMemoryInterface:
    """
    Quantum memory bus interface.

    Implements a CPW bus resonator that couples to:
      - Superconducting data qubits (on-chip)
      - Rare-earth spin ensemble (off-chip or embedded crystal)
      - Optomechanical transducer (for optical frequency conversion)

    The bus resonator is a λ/2 high-Q resonator acting as a
    quantum buffer between the processing and memory layers.
    """
    bus_freq_GHz: float = 5.5
    memory_coupling_MHz: float = 10.0
    n_qubits_coupled: int = 2
    Qi_bus: float = 5e5
    name: str = "MemoryInterface"

    def build(self) -> Component:
        c = gf.Component(self.name)

        # High-Q λ/2 bus resonator
        bus_res = CPWResonator(
            frequency_GHz=self.bus_freq_GHz,
            mode="half",
            Qi_target=self.Qi_bus,
            Qc_target=1e6,
            meander=True,
            meander_width_um=600.0,
            name=f"BusResonator",
        ).build()
        bus_ref = c.add_ref(bus_res)

        # Coupling pads to external memory element
        # (spin ensemble, NV center, etc.)
        for i, y_offset in enumerate([0, 100, 200]):
            pad = c.add_ref(
                gf.components.rectangle(size=(50, 50), layer=LAYER_BASE)
            )
            pad.move((700, y_offset))
            c.add_port(f"memory_port_{i}",
                       center=(750, y_offset + 25), width=50,
                       orientation=0, layer=LAYER_BASE)

        c.add_label(
            text=f"MemInterface\nf={self.bus_freq_GHz}GHz\nQi={self.Qi_bus:.1e}",
            position=(0, -30),
            layer=LAYER_LABEL,
        )
        return c


@dataclass
class RepeaterNode:
    """
    Full quantum repeater node top-level assembly.

    Parameters
    ----------
    n_qubits : int
        Number of data qubits per node (typically 2–8)
    process : str
        Fabrication process identifier
    qubit_freq_GHz : list
        Target qubit frequencies (length = n_qubits)
    readout_freq_GHz : list
        Readout resonator frequencies
    g_MHz : list
        Qubit-resonator coupling strengths
    include_memory : bool
        Include quantum memory interface bus
    include_bsm : bool
        Include Bell-state measurement circuits
    chip_width_um : float
        Physical chip width
    chip_height_um : float
        Physical chip height
    """
    n_qubits: int = 4
    process: str = "Al_Si_150nm"
    qubit_freq_GHz: List[float] = field(
        default_factory=lambda: [4.8, 5.1, 5.4, 5.7]
    )
    readout_freq_GHz: List[float] = field(
        default_factory=lambda: [6.5, 6.7, 6.9, 7.1]
    )
    g_MHz: List[float] = field(
        default_factory=lambda: [80.0, 80.0, 80.0, 80.0]
    )
    qubit_types: List[str] = field(
        default_factory=lambda: ["fixed", "tunable", "fixed", "tunable"]
    )
    include_memory: bool = True
    include_bsm: bool = True
    chip_width_um: float = CHIP_WIDTH_UM
    chip_height_um: float = CHIP_HEIGHT_UM
    name: str = "RepeaterNode"

    def build(self) -> Component:
        c = gf.Component(self.name)

        # ── Chip outline ──────────────────────────────────────
        outline = c.add_ref(
            gf.components.rectangle(
                size=(self.chip_width_um, self.chip_height_um),
                layer=LAYER_DICE,
            )
        )

        # ── Ground plane flood fill ───────────────────────────
        gnd = c.add_ref(
            gf.components.rectangle(
                size=(self.chip_width_um - 2 * EDGE_KEEPOUT,
                      self.chip_height_um - 2 * EDGE_KEEPOUT),
                layer=LAYER_BASE,
            )
        )
        gnd.move((EDGE_KEEPOUT, EDGE_KEEPOUT))

        # ── Flux-trapping holes in ground plane ───────────────
        self._add_flux_holes(c)

        # ── Qubit cells ───────────────────────────────────────
        qubit_cells = []
        for i in range(self.n_qubits):
            qf  = self.qubit_freq_GHz[i] if i < len(self.qubit_freq_GHz) else 5.0
            rf  = self.readout_freq_GHz[i] if i < len(self.readout_freq_GHz) else 6.8
            qtype = self.qubit_types[i] if i < len(self.qubit_types) else "fixed"

            qc = QubitCell(
                qubit_freq_GHz=qf,
                readout_freq_GHz=rf,
                qubit_type=qtype,
                g_MHz=self.g_MHz[i] if i < len(self.g_MHz) else 80.0,
                index=i,
            ).build()

            x_pos = EDGE_KEEPOUT + 500 + i * 1400
            y_pos = self.chip_height_um / 2 - 600

            qc_ref = c.add_ref(qc)
            qc_ref.move((x_pos, y_pos))
            qubit_cells.append(qc_ref)

        # ── SQUID tunable couplers between adjacent qubits ────
        for i in range(self.n_qubits - 1):
            coupler = self._build_tunable_coupler(i)
            coup_ref = c.add_ref(coupler)
            x_coup = EDGE_KEEPOUT + 500 + i * 1400 + 700
            coup_ref.move((x_coup, self.chip_height_um / 2 - 200))

        # ── BSM cells (at each end of the node) ───────────────
        if self.include_bsm:
            bsm_a = BSMCell(freq_GHz=6.0, name="BSM_A").build()
            bsm_b = BSMCell(freq_GHz=6.0, name="BSM_B").build()
            bsm_a_ref = c.add_ref(bsm_a)
            bsm_b_ref = c.add_ref(bsm_b)
            bsm_a_ref.move((EDGE_KEEPOUT + 100,
                             self.chip_height_um - EDGE_KEEPOUT - 400))
            bsm_b_ref.move((self.chip_width_um - EDGE_KEEPOUT - 600,
                             self.chip_height_um - EDGE_KEEPOUT - 400))

        # ── Quantum memory interface ───────────────────────────
        if self.include_memory:
            mem = QuantumMemoryInterface(
                bus_freq_GHz=5.5,
                n_qubits_coupled=self.n_qubits,
            ).build()
            mem_ref = c.add_ref(mem)
            mem_ref.move((EDGE_KEEPOUT + 200, EDGE_KEEPOUT + 200))

        # ── Bond pads ─────────────────────────────────────────
        self._add_bond_pads(c)

        # ── Air-bridge crossovers ─────────────────────────────
        self._add_air_bridges(c)

        # ── Chip label ────────────────────────────────────────
        c.add_label(
            text=(
                f"QR-SC-PDK v2.1.0\n"
                f"RepeaterNode — {self.n_qubits} qubits\n"
                f"Process: {self.process}"
            ),
            position=(self.chip_width_um / 2, self.chip_height_um - 200),
            layer=LAYER_LABEL,
        )

        return c

    def _build_tunable_coupler(self, index: int) -> Component:
        """Build a SQUID-based tunable coupler between qubit[i] and qubit[i+1]."""
        c = gf.Component(f"Coupler_{index}")
        sq = DCSQUID(
            jj_width_nm=350, jj_height_nm=350,
            loop_width_um=6.0, loop_height_um=3.0,
            name=f"CouplerSQUID_{index}",
        ).build()
        c.add_ref(sq)
        # CPW connecting arms
        for x, orient in [(0, 180), (20, 0)]:
            arm = c.add_ref(
                gf.components.rectangle(size=(30, 5), layer=LAYER_BASE)
            )
            arm.move((x, -2.5))
        c.add_port("left",  center=(0, 0), width=5, orientation=180,
                   layer=LAYER_BASE)
        c.add_port("right", center=(50, 0), width=5, orientation=0,
                   layer=LAYER_BASE)
        c.add_port("flux",  center=(25, -20), width=5, orientation=270,
                   layer=LAYER_BASE)
        return c

    def _add_flux_holes(self, c: Component):
        """Add periodic flux-trapping holes in ground plane."""
        hole_d    = 4.0   # µm diameter
        hole_pitch = 50.0  # µm
        x_start = EDGE_KEEPOUT + hole_pitch
        y_start = EDGE_KEEPOUT + hole_pitch

        for ix in range(int((self.chip_width_um - 2*EDGE_KEEPOUT) / hole_pitch)):
            for iy in range(int((self.chip_height_um - 2*EDGE_KEEPOUT) / hole_pitch)):
                x = x_start + ix * hole_pitch
                y = y_start + iy * hole_pitch
                hole = c.add_ref(
                    gf.components.circle(radius=hole_d / 2, layer=LAYER_HOLES)
                )
                hole.move((x, y))

    def _add_bond_pads(self, c: Component):
        """Add wire-bond pads around the chip periphery."""
        pads_per_side = 12
        for i in range(pads_per_side):
            # Bottom row
            x = EDGE_KEEPOUT + i * PAD_PITCH_UM + PAD_PITCH_UM / 2
            pad_b = c.add_ref(
                gf.components.rectangle(
                    size=(PAD_SIZE_UM, PAD_SIZE_UM), layer=LAYER_PAD
                )
            )
            pad_b.move((x - PAD_SIZE_UM / 2, EDGE_KEEPOUT / 2 - PAD_SIZE_UM / 2))

            # Top row
            pad_t = c.add_ref(
                gf.components.rectangle(
                    size=(PAD_SIZE_UM, PAD_SIZE_UM), layer=LAYER_PAD
                )
            )
            pad_t.move((x - PAD_SIZE_UM / 2,
                         self.chip_height_um - EDGE_KEEPOUT / 2 - PAD_SIZE_UM / 2))

            # Labels
            c.add_label(f"BP_{i}B", (x, EDGE_KEEPOUT / 2), layer=LAYER_LABEL)
            c.add_label(f"BP_{i}T", (x, self.chip_height_um - EDGE_KEEPOUT / 2),
                        layer=LAYER_LABEL)

    def _add_air_bridges(self, c: Component):
        """Add air-bridge crossovers on CPW lines (suppress slot-line modes)."""
        bridge_w  = 10.0
        bridge_h  = 20.0
        # Simplified: place bridges every 200 µm along horizontal CPW lines
        y_cpw = self.chip_height_um / 2 - 500
        x = EDGE_KEEPOUT + 400
        while x < self.chip_width_um - EDGE_KEEPOUT - 200:
            ab = c.add_ref(
                gf.components.rectangle(size=(bridge_w, bridge_h), layer=LAYER_AB)
            )
            ab.move((x - bridge_w / 2, y_cpw - bridge_h / 2))
            x += 200.0

    def generate_report(self) -> Dict:
        """Generate a design parameter report."""
        from models.hamiltonian.transmon_ham import TransmonHamiltonian, RepeaterNodeHamiltonian
        report = {
            "chip": {
                "width_mm": self.chip_width_um / 1e3,
                "height_mm": self.chip_height_um / 1e3,
                "process": self.process,
                "n_qubits": self.n_qubits,
            },
            "qubits": [],
        }
        for i in range(self.n_qubits):
            qf = self.qubit_freq_GHz[i] if i < len(self.qubit_freq_GHz) else 5.0
            th = TransmonHamiltonian(EC_MHz=250, EJ_GHz=15.0)
            report["qubits"].append({
                "index": i,
                "freq_GHz": qf,
                "type": self.qubit_types[i] if i < len(self.qubit_types) else "fixed",
                "EC_MHz": th.EC_MHz,
                "EJ_GHz": round(th.EJ_GHz, 3),
                "anharmonicity_MHz": round(th.anharmonicity_MHz, 1),
            })

        node_h = RepeaterNodeHamiltonian(
            qubit_freqs_GHz=self.qubit_freq_GHz,
            resonator_freqs_GHz=self.readout_freq_GHz,
            g_MHz_list=self.g_MHz,
        )
        report["hamiltonian"] = node_h.node_summary()
        return report


if __name__ == "__main__":
    import json

    node = RepeaterNode(
        n_qubits=4,
        process="Al_Si_150nm",
        qubit_freq_GHz=[4.8, 5.1, 5.4, 5.7],
        readout_freq_GHz=[6.5, 6.7, 6.9, 7.1],
        g_MHz=[80.0, 80.0, 80.0, 80.0],
        qubit_types=["fixed", "tunable", "fixed", "tunable"],
        include_memory=True,
        include_bsm=True,
    )

    print("Building repeater node layout...")
    try:
        chip = node.build()
        chip.write_gds("repeater_node.gds")
        print("GDS written to: repeater_node.gds")
    except Exception as e:
        print(f"GDS build skipped (gdsfactory not installed): {e}")

    report = node.generate_report()
    print("\nDesign Report:")
    print(json.dumps(report, indent=2))
