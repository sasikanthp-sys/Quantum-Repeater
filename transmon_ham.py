"""
models/hamiltonian/transmon_ham.py
Transmon Qubit Hamiltonian Model
Uses QuTiP (Quantum Toolbox in Python) ≥ 5.x

Implements:
  1. Full Cooper-pair box / transmon Hamiltonian
  2. Jaynes-Cummings (JC) qubit-resonator Hamiltonian
  3. Dispersive approximation
  4. Lindblad master equation for T1/T2 decay
  5. Steady-state and time-domain solver interfaces

References:
  - Koch et al., PRA 76, 042319 (2007)
  - Blais et al., PRA 69, 062320 (2004)
  - Krantz et al., Appl. Phys. Rev. 6, 021318 (2019)
"""

from __future__ import annotations
import math
import numpy as np
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

try:
    import qutip as qt
    QUTIP_AVAILABLE = True
except ImportError:
    QUTIP_AVAILABLE = False
    print("WARNING: QuTiP not installed. Install with: pip install qutip")

# ── Physical constants ────────────────────────────────────────
H_PLANCK = 6.62607015e-34   # J·s
HBAR     = H_PLANCK / (2 * math.pi)
E_CHARGE = 1.602176634e-19  # C
PHI0     = 2.067833848e-15  # Wb (flux quantum)
KB       = 1.380649e-23     # J/K


# ═══════════════════════════════════════════════════════════════
# 1. Cooper-Pair Box / Transmon Hamiltonian
# ═══════════════════════════════════════════════════════════════

@dataclass
class TransmonHamiltonian:
    """
    Full transmon Hamiltonian in the charge basis.

    H = 4 EC (n̂ - ng)² - EJ cos(φ̂)

    In the charge basis |N⟩ (N = Cooper pairs on island):
      ⟨N| 4EC(n̂-ng)² |N⟩  = 4 EC (N - ng)²
      ⟨N| -EJ cos(φ̂) |N'⟩ = -EJ/2 × (δ_{N,N'+1} + δ_{N,N'-1})

    Parameters
    ----------
    EC_MHz : float
        Charging energy in MHz (EC = e²/2C)
    EJ_GHz : float
        Josephson energy in GHz
    ng : float
        Offset charge (in units of 2e), gate voltage parameter
    N_max : int
        Charge basis truncation: |N| ≤ N_max
    N_fock : int
        Truncation of transmon energy levels (for coupling calculations)
    """
    EC_MHz: float = 250.0
    EJ_GHz: float = 15.0
    ng: float = 0.0
    N_max: int = 10        # charge basis: -N_max to N_max
    N_fock: int = 5        # keep lowest N_fock levels

    def __post_init__(self):
        self.EC_GHz = self.EC_MHz * 1e-3
        self.N_dim  = 2 * self.N_max + 1
        self._build_hamiltonian()

    def _build_hamiltonian(self):
        """Construct H in charge basis and diagonalize."""
        if not QUTIP_AVAILABLE:
            self._fallback_spectrum()
            return

        N = self.N_dim
        # Charge operator in charge basis
        n_vals = np.arange(-self.N_max, self.N_max + 1)

        # Diagonal: 4 EC (N - ng)²
        diag = 4.0 * self.EC_GHz * (n_vals - self.ng) ** 2
        H_charge = qt.Qobj(np.diag(diag))

        # Off-diagonal: -EJ/2 (hopping ±1)
        off_diag = np.zeros((N, N))
        for i in range(N - 1):
            off_diag[i, i + 1] = -self.EJ_GHz / 2
            off_diag[i + 1, i] = -self.EJ_GHz / 2
        H_josephson = qt.Qobj(off_diag)

        self.H_full = H_charge + H_josephson

        # Eigenvalues (energy levels in GHz)
        self.eigenvalues, self.eigenstates = self.H_full.eigenstates()
        self.eigenvalues -= self.eigenvalues[0]   # set ground state to 0

        # Transition frequencies
        self.f_01_GHz = float(self.eigenvalues[1])
        self.f_12_GHz = float(self.eigenvalues[2] - self.eigenvalues[1])
        self.anharmonicity_MHz = (self.f_12_GHz - self.f_01_GHz) * 1e3

    def _fallback_spectrum(self):
        """Approximate energy spectrum without QuTiP."""
        # Approximate transmon spectrum (Koch et al. Eq. 2.11)
        EJ = self.EJ_GHz
        EC = self.EC_GHz
        # E_m ≈ -EJ + √(8 EC EJ) (m + 1/2) - EC/12 (6m² + 6m + 3) (EJ/8EC)^(1/2)
        def E_m(m):
            return (-EJ
                    + math.sqrt(8 * EC * EJ) * (m + 0.5)
                    - EC / 12 * (6 * m**2 + 6*m + 3) * (EJ / (8*EC))**0.5)
        self.eigenvalues = np.array([E_m(m) for m in range(self.N_fock)])
        self.eigenvalues -= self.eigenvalues[0]
        self.f_01_GHz = float(self.eigenvalues[1])
        self.f_12_GHz = float(self.eigenvalues[2] - self.eigenvalues[1])
        self.anharmonicity_MHz = (self.f_12_GHz - self.f_01_GHz) * 1e3

    def charge_dispersion_MHz(self) -> float:
        """
        Charge dispersion ε_m = max_ng(E_m) - min_ng(E_m).
        For transmon: exponentially suppressed with √(EJ/8EC).
        """
        # Approximate: ε_01 ≈ (-1)^1 × EC × (2^4/√(2π)) × (EJ/2EC)^(3/4)
        #              × exp(-√(8 EJ/EC))
        x = math.sqrt(8 * self.EJ_GHz / self.EC_GHz)
        eps = (self.EC_GHz * 1e3 * (2**4 / math.sqrt(2 * math.pi)) *
               (self.EJ_GHz / (2 * self.EC_GHz)) ** 0.75 * math.exp(-x))
        return abs(eps)  # MHz

    def matrix_element_01(self) -> float:
        """
        |⟨1|n̂|0⟩|² — charge matrix element for drive coupling.
        For transmon: ≈ (EJ / 32 EC)^(1/4) / 2
        """
        return (self.EJ_GHz / (32 * self.EC_GHz)) ** 0.25 / 2

    def summary(self) -> dict:
        return {
            "EC_MHz": round(self.EC_MHz, 1),
            "EJ_GHz": round(self.EJ_GHz, 3),
            "EJ_over_EC": round(self.EJ_GHz / self.EC_GHz, 1),
            "f_01_GHz": round(self.f_01_GHz, 4),
            "f_12_GHz": round(self.f_12_GHz, 4),
            "anharmonicity_MHz": round(self.anharmonicity_MHz, 1),
            "charge_dispersion_MHz": round(self.charge_dispersion_MHz(), 4),
            "matrix_element_01": round(self.matrix_element_01(), 4),
        }


# ═══════════════════════════════════════════════════════════════
# 2. Jaynes-Cummings Hamiltonian (Qubit + Resonator)
# ═══════════════════════════════════════════════════════════════

@dataclass
class JaynesCummingsModel:
    """
    Jaynes-Cummings / Tavis-Cummings Hamiltonian.

    H = ωr â†â + ωq σ+σ- + g (â†σ- + â σ+)   [rotating wave approx]

    Parameters
    ----------
    qubit_freq_GHz : float
        Qubit 01 transition frequency
    resonator_freq_GHz : float
        Readout resonator frequency
    g_MHz : float
        Qubit-resonator coupling strength
    n_fock : int
        Fock space truncation (photon number)
    n_levels : int
        Qubit level truncation (2 for TLS, 3+ for transmon)
    kerr_MHz : float
        Qubit self-Kerr (anharmonicity) for transmon correction
    """
    qubit_freq_GHz: float = 5.0
    resonator_freq_GHz: float = 6.8
    g_MHz: float = 80.0
    n_fock: int = 10
    n_levels: int = 3        # 3 for transmon (|0⟩, |1⟩, |2⟩)
    kerr_MHz: float = -250.0  # anharmonicity

    def __post_init__(self):
        self.detuning_GHz = self.qubit_freq_GHz - self.resonator_freq_GHz
        self.chi_MHz = self._dispersive_shift()

    def _dispersive_shift(self) -> float:
        """
        Dispersive shift χ in dispersive regime (g << |Δ|).
        χ ≈ g² / Δ × (α / (Δ + α))   [transmon correction]

        where Δ = ωq - ωr, α = anharmonicity
        """
        g  = self.g_MHz * 1e-3   # GHz
        D  = self.detuning_GHz   # GHz
        a  = self.kerr_MHz * 1e-3  # GHz
        if abs(D) < 0.1:
            return float('nan')  # too close to resonance
        chi = (g**2 / D) * (a / (D + a))
        return chi * 1e3  # MHz

    def build_hamiltonian(self):
        """Return H, collapse operators for QuTiP simulation."""
        if not QUTIP_AVAILABLE:
            raise ImportError("QuTiP required for Hamiltonian simulation")

        ωr = 2 * math.pi * self.resonator_freq_GHz  # GHz (ℏ=1)
        ωq = 2 * math.pi * self.qubit_freq_GHz
        g  = 2 * math.pi * self.g_MHz * 1e-3

        # Operators
        a   = qt.tensor(qt.destroy(self.n_fock), qt.qeye(self.n_levels))
        adag= a.dag()
        q   = qt.tensor(qt.qeye(self.n_fock), qt.destroy(self.n_levels))
        qdag= q.dag()

        # Hamiltonian
        H = (ωr * adag * a
             + ωq * qdag * q
             + g * (adag * q + a * qdag))

        # Transmon correction: Kerr nonlinearity
        if self.n_levels >= 3:
            alpha = 2 * math.pi * self.kerr_MHz * 1e-3
            H += (alpha / 2) * qdag * qdag * q * q

        return H

    def dispersive_hamiltonian(self):
        """
        Effective dispersive Hamiltonian (4th order perturbation theory).
        H_disp = ωr' â†â + ωq' σ+σ- + χ â†â σz
        """
        if not QUTIP_AVAILABLE:
            raise ImportError("QuTiP required")

        chi = 2 * math.pi * self.chi_MHz * 1e-3  # GHz
        ωr_p = 2 * math.pi * self.resonator_freq_GHz
        ωq_p = 2 * math.pi * self.qubit_freq_GHz

        a    = qt.tensor(qt.destroy(self.n_fock), qt.qeye(2))
        adag = a.dag()
        sz   = qt.tensor(qt.qeye(self.n_fock), qt.sigmaz())

        H_disp = ωr_p * adag * a + 0.5 * ωq_p * sz + chi * adag * a * sz
        return H_disp

    def summary(self) -> dict:
        return {
            "qubit_freq_GHz": self.qubit_freq_GHz,
            "resonator_freq_GHz": self.resonator_freq_GHz,
            "detuning_GHz": round(self.detuning_GHz, 4),
            "g_MHz": self.g_MHz,
            "dispersive_shift_chi_MHz": round(self.chi_MHz, 3),
            "cooperativity_4g2_kapkap": None,  # requires κ info
        }


# ═══════════════════════════════════════════════════════════════
# 3. Lindblad Master Equation Solver
# ═══════════════════════════════════════════════════════════════

@dataclass
class LindbladSolver:
    """
    Lindblad master equation for open quantum system dynamics.

    dρ/dt = -i [H, ρ] + Σ_k γ_k (L_k ρ L_k† - ½{L_k†L_k, ρ})

    Dissipation channels:
      - T1 (energy relaxation): rate γ₁ = 1/T1
      - Tφ (pure dephasing): rate γφ = 1/Tφ
      - κ (cavity decay): rate κ = ωr/Qc
      - κ_int (internal cavity loss): rate κi = ωr/Qi
    """
    jc_model: JaynesCummingsModel = field(default_factory=JaynesCummingsModel)
    T1_us: float = 100.0          # qubit energy relaxation time
    T2_us: float = 200.0          # qubit total coherence time
    kappa_MHz: float = 2.0        # cavity linewidth (κ/2π)
    kappa_int_MHz: float = 0.02   # internal cavity loss (κi/2π)
    temperature_mK: float = 20.0  # thermal occupancy

    def __post_init__(self):
        # Derived rates
        self.gamma1_MHz   = 1.0 / (self.T1_us * 1e3)   # 1/µs → MHz
        T_phi_us = 1.0 / (1.0/self.T2_us - 0.5/self.T1_us)
        self.gamma_phi_MHz = 1.0 / (T_phi_us * 1e3)
        self.n_th = self._thermal_occupancy()

    def _thermal_occupancy(self) -> float:
        """Mean thermal photon number at operating temperature."""
        kT = KB * self.temperature_mK * 1e-3
        hω = H_PLANCK * self.jc_model.qubit_freq_GHz * 1e9
        if kT / hω < 1e-6:
            return 0.0
        return 1.0 / (math.exp(hω / kT) - 1)

    def build_collapse_operators(self) -> list:
        """Return list of Lindblad collapse operators."""
        if not QUTIP_AVAILABLE:
            raise ImportError("QuTiP required")

        nf = self.jc_model.n_fock
        nl = self.jc_model.n_levels
        n_th = self.n_th

        # Qubit operators
        sm = qt.tensor(qt.qeye(nf), qt.destroy(nl))  # σ-
        sp = sm.dag()
        sz = qt.tensor(qt.qeye(nf), qt.sigmaz() if nl == 2
                        else (qt.num(nl) * 2 - qt.qeye(nl)))

        # Cavity operator
        a = qt.tensor(qt.destroy(nf), qt.qeye(nl))

        gamma1  = 2 * math.pi * self.gamma1_MHz * 1e-3   # GHz
        gammaphi= 2 * math.pi * self.gamma_phi_MHz * 1e-3
        kappa   = 2 * math.pi * self.kappa_MHz * 1e-3
        kappa_i = 2 * math.pi * self.kappa_int_MHz * 1e-3

        c_ops = [
            # Qubit relaxation T1
            math.sqrt(gamma1 * (1 + n_th)) * sm,
            math.sqrt(gamma1 * n_th) * sp,
            # Pure dephasing Tφ
            math.sqrt(gammaphi) * sz,
            # Cavity decay (external coupling)
            math.sqrt(kappa) * a,
            # Cavity internal loss
            math.sqrt(kappa_i) * a,
        ]
        return c_ops

    def simulate_rabi(self, omega_drive_MHz: float, pulse_length_ns: float,
                       n_points: int = 200) -> Tuple:
        """
        Simulate Rabi oscillation driven at omega_drive.
        Returns (times_ns, populations_0, populations_1)
        """
        if not QUTIP_AVAILABLE:
            raise ImportError("QuTiP required")

        H0 = self.jc_model.build_hamiltonian()
        c_ops = self.build_collapse_operators()

        # Drive term: H_drive = Ω/2 × (σ+ + σ-) × cos(ωd t)
        nf = self.jc_model.n_fock
        nl = self.jc_model.n_levels
        sm = qt.tensor(qt.qeye(nf), qt.destroy(nl))
        H_drive = sm + sm.dag()

        Omega = 2 * math.pi * omega_drive_MHz * 1e-3  # GHz
        H = [H0, [H_drive, f"cos({omega_drive_MHz}*t)"]]  # TD Hamiltonian

        psi0 = qt.tensor(qt.basis(nf, 0), qt.basis(nl, 0))  # |0,0⟩
        tlist = np.linspace(0, pulse_length_ns, n_points)

        result = qt.mesolve(H0, psi0, tlist, c_ops,
                             e_ops=[sm.dag() * sm])
        return tlist, result.expect[0]

    def T1_measurement(self, t_max_us: float = 300.0,
                        n_points: int = 300) -> Tuple:
        """Simulate T1 decay: prepare |1⟩, measure vs time."""
        if not QUTIP_AVAILABLE:
            raise ImportError("QuTiP required")

        H = self.jc_model.build_hamiltonian()
        c_ops = self.build_collapse_operators()
        nf = self.jc_model.n_fock
        nl = self.jc_model.n_levels
        sm = qt.tensor(qt.qeye(nf), qt.destroy(nl))

        # Prepare qubit in |1⟩
        psi0 = qt.tensor(qt.basis(nf, 0), qt.basis(nl, 1))
        tlist = np.linspace(0, t_max_us * 1e3, n_points)  # ns

        result = qt.mesolve(H, psi0, tlist, c_ops,
                             e_ops=[sm.dag() * sm])
        return tlist / 1e3, result.expect[0]  # µs, P_1


# ═══════════════════════════════════════════════════════════════
# 4. Full Repeater Node Hamiltonian
# ═══════════════════════════════════════════════════════════════

@dataclass
class RepeaterNodeHamiltonian:
    """
    Multi-qubit Hamiltonian for quantum repeater node.

    For N qubits coupled to M readout resonators, with
    qubit-qubit couplers (tunable via SQUID):

    H = Σᵢ ωᵢ σᵢ⁺σᵢ⁻
      + Σⱼ ωʲᵣ aⱼ†aⱼ
      + Σᵢ gᵢ (aᵢ†σᵢ⁻ + aᵢ σᵢ⁺)        (qubit-resonator)
      + Σ<ij> Jᵢⱼ (σᵢ⁺σⱼ⁻ + σᵢ⁻σⱼ⁺)     (qubit-qubit ZZ via coupler)

    Parameters
    ----------
    qubit_freqs_GHz : list
        Frequencies of N qubits
    resonator_freqs_GHz : list
        Frequencies of M readout resonators (len = N)
    g_MHz_list : list
        Qubit-resonator coupling strengths
    J_MHz_matrix : 2D array
        Qubit-qubit coupling matrix Jᵢⱼ [MHz]
    """
    qubit_freqs_GHz: List[float] = field(
        default_factory=lambda: [4.8, 5.1, 5.4, 5.7]
    )
    resonator_freqs_GHz: List[float] = field(
        default_factory=lambda: [6.5, 6.7, 6.9, 7.1]
    )
    g_MHz_list: List[float] = field(
        default_factory=lambda: [80.0, 80.0, 80.0, 80.0]
    )
    J_MHz_matrix: Optional[np.ndarray] = None
    n_fock: int = 5
    n_qlevels: int = 2

    def __post_init__(self):
        self.N = len(self.qubit_freqs_GHz)
        if self.J_MHz_matrix is None:
            self.J_MHz_matrix = np.zeros((self.N, self.N))
        # Default nearest-neighbor ZZ: J01, J12, J23 = 5 MHz
        for i in range(self.N - 1):
            self.J_MHz_matrix[i, i+1] = 5.0
            self.J_MHz_matrix[i+1, i] = 5.0

    def zz_coupling_MHz(self, i: int, j: int) -> float:
        """
        ZZ coupling between qubits i and j via virtual
        photon exchange through shared bus resonator.
        """
        gi = self.g_MHz_list[i] * 1e-3
        gj = self.g_MHz_list[j] * 1e-3
        Di = self.qubit_freqs_GHz[i] - self.resonator_freqs_GHz[i]
        Dj = self.qubit_freqs_GHz[j] - self.resonator_freqs_GHz[j]
        # J_eff ≈ gi gj (1/Di + 1/Dj) / 2
        J_eff = gi * gj * (1/Di + 1/Dj) / 2
        return J_eff * 1e3  # MHz

    def node_summary(self) -> dict:
        zz = {}
        for i in range(self.N):
            for j in range(i+1, self.N):
                zz[f"ZZ_{i}{j}_MHz"] = round(self.zz_coupling_MHz(i, j), 3)

        return {
            "N_qubits": self.N,
            "qubit_freqs_GHz": self.qubit_freqs_GHz,
            "resonator_freqs_GHz": self.resonator_freqs_GHz,
            "g_MHz": self.g_MHz_list,
            "ZZ_couplings": zz,
        }


if __name__ == "__main__":
    # Transmon parameters
    th = TransmonHamiltonian(EC_MHz=250, EJ_GHz=15.0)
    print("Transmon:", th.summary())

    # Jaynes-Cummings
    jc = JaynesCummingsModel(qubit_freq_GHz=5.0, resonator_freq_GHz=6.8, g_MHz=80)
    print("JC model:", jc.summary())

    # Repeater node
    node = RepeaterNodeHamiltonian()
    print("Repeater node:", node.node_summary())
