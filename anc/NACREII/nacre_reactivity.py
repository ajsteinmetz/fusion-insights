
"""
nacre_reactivity.py — Reaction-agnostic utilities to read NACRE II rates
and compute reactivities and simple power scalings.

CSV format expected:
    T9,adopted,low,high
Units:
    NACRE II provides N_A⟨σv⟩ in cm^3 mol^-1 s^-1.
    This module returns ⟨σv⟩ in m^3 s^-1 (pair-averaged).

This version is reaction-agnostic (no DT-specific energies or stoichiometry).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Tuple

import numpy as np
import pandas as pd
from scipy.interpolate import PchipInterpolator

# ---------- Physical constants (shared) ----------
N_A = 6.02214076e23         # mol^-1
KEV_TO_K = 1.16045e7        # K per keV
MEV_TO_J = 1.602176634e-13  # J per MeV

Which = Literal["adopted", "low", "high"]


@dataclass
class NacreRate:
    """Container for a single NACRE II rate table with log-log PCHIP interpolation."""
    T9: np.ndarray          # Temperature in 10^9 K
    NA_sigmav: np.ndarray   # N_A⟨σv⟩ in cm^3 mol^-1 s^-1 (chosen column)
    which: Which = "adopted"

    # ---- interpolation ----
    def _interp(self):
        x = np.log(self.T9)
        y = np.log(self.NA_sigmav)
        return PchipInterpolator(x, y, extrapolate=True)

    # ---- reactivities ----
    def NA_sigmav_T9(self, T9):
        """Return N_A⟨σv⟩(T9) in cm^3 mol^-1 s^-1."""
        T9 = np.asarray(T9, dtype=float)
        y = self._interp()(np.log(T9))
        return np.exp(y)

    def sigmav_T9(self, T9):
        """Return ⟨σv⟩(T9) in m^3 s^-1 (pair-averaged)."""
        NA_sv = self.NA_sigmav_T9(T9)   # cm^3 mol^-1 s^-1
        sv_cm = NA_sv / N_A             # cm^3 s^-1
        return sv_cm * 1e-6             # m^3 s^-1

    def sigmav_keV(self, T_keV):
        """Return ⟨σv⟩(T_keV) in m^3 s^-1 (pair-averaged)."""
        T_keV = np.asarray(T_keV, dtype=float)
        T9 = (T_keV * KEV_TO_K) / 1e9
        return self.sigmav_T9(T9)


# ---------- Stoichiometry helpers ----------
def composition_coeff(ZA: int, ZB: int, r: float) -> float:
    """
    Return the composition coefficient C such that
        n_A n_B = C * n_e^2
    for a binary, quasi-neutral plasma with ion charges Z_A, Z_B and ratio r = n_A/n_B.

    Derivation:
        n_e = Z_A n_A + Z_B n_B,  n_A = r n_B  ⇒  n_e = (Z_A r + Z_B) n_B
        n_A n_B = r n_B^2 = r * (n_e / (Z_A r + Z_B))^2
        ⇒ C = r / (Z_A r + Z_B)^2
    """
    ZA = float(ZA); ZB = float(ZB); r = float(r)
    return r / (ZA * r + ZB)**2


def zeff(ZA: int, ZB: int, r: float) -> float:
    """
    Return Z_eff = (Σ n_j Z_j^2) / (Σ n_j Z_j) for a binary mixture (A,B) with r = n_A/n_B.
    """
    ZA = float(ZA); ZB = float(ZB); r = float(r)
    # up to an overall factor n_B which cancels:
    num = r * ZA**2 + 1.0 * ZB**2
    den = r * ZA    + 1.0 * ZB
    return num / den


# ---------- Bremsstrahlung (density-normalized) ----------
def brem_per_ne2(
    T_keV,
    Z_eff: float = 1.0,
    gB: float = 1.2,
    include_ee: bool = True,
):
    """
    Density-normalized bremsstrahlung loss P_brem / n_e^2  [W m^3]
    Uses a practical NRL/Wesson-like form with Te in eV:

        P_brem / n_e^2 = Cb * Z_eff * sqrt(Te[eV]) * gB * (1 + a_ee * Te[eV])

    where:
      - Cb   = 1.69e-38  W m^3 eV^{-1/2}
      - a_ee = 5.1e-6    (electron–electron correction)
      - gB   ~ 1.1–1.3   (Gaunt factor)
    """
    Cb = 1.69e-38
    a_ee = 5.1e-6

    Te_eV = 1e3 * np.asarray(T_keV, dtype=float)     # keV -> eV
    Pbrem = Cb * Z_eff * np.sqrt(Te_eV) * gB         # e–i term

    if include_ee:
        Pbrem *= (1.0 + a_ee * Te_eV)                # add e–e correction

    return Pbrem


# ---------- Convenience: density-normalized power for arbitrary channels ----------
def power_per_ne2(T_keV, sv_m3_per_s, Q_Joule: float, C: float) -> np.ndarray:
    """
    P / n_e^2  =  C * ⟨σv⟩(T) * Q      [W m^3]

    Parameters
    ----------
    T_keV : array-like (unused here; included for symmetry)
    sv_m3_per_s : array-like
        Reactivity in m^3/s.
    Q_Joule : float
        Energy released per reaction in Joules (choose α-heating fraction if desired).
    C : float
        Composition coefficient such that n_A n_B = C * n_e^2.
    """
    return C * np.asarray(sv_m3_per_s, dtype=float) * float(Q_Joule)


def load_nacre_rates(csv_path, which: Which = "adopted") -> NacreRate:
    """
    Load a NACRE II rate table from CSV and return a NacreRate object.

    Parameters
    ----------
    csv_path : path to CSV with columns T9, adopted, low, high
    which    : which column to use ("adopted", "low", "high")
    """
    df = pd.read_csv(csv_path)
    required = {"T9", "adopted", "low", "high"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    df = df.sort_values("T9")
    return NacreRate(df["T9"].to_numpy(), df[which].to_numpy(), which=which)


__all__ = [
    "N_A", "KEV_TO_K", "MEV_TO_J",
    "NacreRate", "load_nacre_rates",
    "composition_coeff", "zeff",
    "brem_per_ne2", "power_per_ne2",
]
