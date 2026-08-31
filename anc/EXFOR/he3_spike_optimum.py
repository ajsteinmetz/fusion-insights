#!/usr/bin/env python3
"""Optimal ${}^3$He spike fraction and burn temperature for a d-3He plasma.

Produces the numbers of table 'tab:He3Spike' in aneutronic-fusion-v3.tex: for
each ${}^3$He number fraction x the temperature T_opt that maximizes the
heating-to-bremsstrahlung ratio

    G(x,T) = P_fus / P_brem ,

the maximum G_max, and the neutron energy fraction f_n, both for the primary
reactions alone and in the strong secondary burn-up limit chi_t, chi_3 >> 1.

Cross sections
--------------
Bosch-Hale sigma(E) from bosch_hale.py in this directory; reactivities are
obtained by direct Maxwellian averaging over the centre-of-mass energy,

    <sigma v>(T) = sqrt(8/(pi mu)) (kT)^{-3/2} int sigma(E) E exp(-E/kT) dE .

Checks against the standard values: <sigma v>_dt = 1.14e-22 m^3/s at 10 keV
peaking at 66 keV, <sigma v>_dd = 1.19e-24 m^3/s at 10 keV, and the d+3He
reactivity peaking near 240 keV.  The temperature scan stops at 300 keV, well
inside the fitted range of the Bosch-Hale coefficient sets (0.3-900 keV for
3He(d,p), 0.5-4900 keV for the dd branches).

Composition
-----------
At fixed electron density, with x = n_3/(n_d + n_3) and n_e = n_d + 2 n_3,

    n_d/n_e = (1-x)/(1+x),   n_3/n_e = x/(1+x),   Z_eff = (1+3x)/(1+x),

so the dd rate carries [(1-x)/(1+x)]^2 and the d+3He rate x(1-x)/(1+x)^2.

Bremsstrahlung
--------------
Eq.(eq:powerBrem) of the manuscript,
P_brem/n_e^2 = Cb Z_eff sqrt(Te) (1 + a1 Te/me c^2) gB, with Te in keV.

Usage
-----
    python he3_spike_optimum.py            # table rows plus the global optimum
    python he3_spike_optimum.py --checks   # also print the reactivity checks
"""
import sys

import numpy as np

import bosch_hale as bh

U = 931494.10242            # keV/c^2 per atomic mass unit
C_LIGHT = 2.99792458e8      # m/s
M_D, M_T, M_HE3 = 2.013553, 3.016049, 3.016029   # u

MU_DD = M_D / 2.0
MU_D3 = M_D * M_HE3 / (M_D + M_HE3)
MU_DT = M_D * M_T / (M_D + M_T)

MEV_J = 1.602176634e-13
Q_DDP, Q_DDN, Q_D3, Q_DT = 4.033, 3.269, 18.35, 17.59     # MeV, total release
ECH_DDP, ECH_DDN = 4.033, 0.82        # charged-particle share of the dd branches
ECH_D3, ECH_DT = 18.35, 3.56          # ... of d+3He and d+t
EN_DDN, EN_DT = 2.45, 14.03           # neutron energies

CB, A1, GB, MEC2 = 4.83e-37, 2.6, 1.1, 511.0      # Eq.(eq:powerBrem)


# ---------------------------------------------------------------- reactivity
def sigma_m2(name, E):
    """Bosch-Hale cross section [m^2] on an array of c.m. energies E [keV]."""
    BG, A, B, _ = bh.REACTIONS[name]
    num = A[0] + E * (A[1] + E * (A[2] + E * (A[3] + E * A[4])))
    den = 1.0 + E * (B[0] + E * (B[1] + E * (B[2] + E * B[3])))
    sigma_mb = (num / den) / (E * np.exp(BG / np.sqrt(E)))
    return np.maximum(sigma_mb, 0.0) * 1e-31          # mb -> m^2


def sigmav(name, T, mu_u, Emin=0.4, Emax=4000.0, nE=6000):
    """Maxwellian reactivity <sigma v>(T) [m^3/s], vectorized in T [keV]."""
    E = np.logspace(np.log10(Emin), np.log10(Emax), nE)
    sig = sigma_m2(name, E)
    T = np.atleast_1d(np.asarray(T, float))
    integ = np.trapezoid(sig * E * np.exp(-E[None, :] / T[:, None]), E, axis=1)
    pref = np.sqrt(8.0 / (np.pi * mu_u * U)) * C_LIGHT
    return pref * T**-1.5 * integ


T = np.logspace(np.log10(3.0), np.log10(300.0), 4000)     # keV
SV_DDP = sigmav("D(d,p)T", T, MU_DD)
SV_DDN = sigmav("D(d,n)3He", T, MU_DD)
SV_D3 = sigmav("3He(d,p)4He", T, MU_D3, Emax=900.0)
SV_DT = sigmav("T(d,n)4He", T, MU_DT, Emax=550.0)


# ---------------------------------------------------------------- power balance
def zeff(x):
    return (1.0 + 3.0 * x) / (1.0 + x)


def brem(T, x):
    """P_brem / n_e^2 [W m^3], Eq.(eq:powerBrem)."""
    return CB * zeff(x) * np.sqrt(T) * (1.0 + A1 * T / MEC2) * GB


def powers(x, sel=slice(None)):
    """Density-normalized rates and powers per n_e^2 on the temperature grid.

    'full' quantities are the strong burn-up limit chi_t, chi_3 >> 1, in which
    every dd->p+t triton burns as d+t (14 MeV neutron) and every dd->n+3He
    helion burns as d+3He (aneutronic).
    """
    fd = (1.0 - x) / (1.0 + x)
    f3 = x / (1.0 + x)
    Rddp = 0.5 * fd**2 * SV_DDP[sel]
    Rddn = 0.5 * fd**2 * SV_DDN[sel]
    Rd3 = fd * f3 * SV_D3[sel]
    P_ch = (Rddp * ECH_DDP + Rddn * ECH_DDN + Rd3 * ECH_D3) * MEV_J
    E_tot = (Rddp * Q_DDP + Rddn * Q_DDN + Rd3 * Q_D3) * MEV_J
    E_n = Rddn * EN_DDN * MEV_J
    return dict(
        Rddp=Rddp, Rddn=Rddn, Rd3=Rd3,
        P_ch=P_ch, E_tot=E_tot, E_n=E_n,
        P_ch_full=P_ch + (Rddp * ECH_DT + Rddn * ECH_D3) * MEV_J,
        E_tot_full=E_tot + (Rddp * Q_DT + Rddn * Q_D3) * MEV_J,
        E_n_full=E_n + Rddp * EN_DT * MEV_J,
    )


def gain(x, full=False):
    """G(x,T) = P_fus / P_brem on the temperature grid."""
    p = powers(x)
    return (p["P_ch_full"] if full else p["P_ch"]) / brem(T, x)


def optimum(x, full=False):
    """(T_opt [keV], G_max, f_n) maximizing G over temperature at fixed x."""
    G = gain(x, full)
    i = int(np.argmax(G))
    p = powers(x, slice(i, i + 1))
    fn = (p["E_n_full"][0] / p["E_tot_full"][0] if full
          else p["E_n"][0] / p["E_tot"][0])
    return T[i], G[i], fn


# ---------------------------------------------------------------- output
def checks():
    print("Reactivities <sigma v> [m^3/s] (Bosch-Hale sigma, Maxwell average)\n")
    print("  T[keV]      dd(p,t)      dd(n,3He)       dd sum          d3He"
          "            dt")
    for t in (5.0, 10.0, 20.0, 50.0, 100.0, 200.0):
        i = int(np.argmin(abs(T - t)))
        print("  %6.1f  %.4e  %.4e  %.4e  %.4e  %.4e"
              % (T[i], SV_DDP[i], SV_DDN[i], SV_DDP[i] + SV_DDN[i],
                 SV_D3[i], SV_DT[i]))
    print("\n  <sv> peaks:  d3He at %.0f keV,  dt at %.0f keV"
          % (T[int(np.argmax(SV_D3))], T[int(np.argmax(SV_DT))]))
    print("  reference:   dt = 1.1e-22 m^3/s at 10 keV, peak near 65 keV;"
          "  dd sum = 1.2e-24 m^3/s at 10 keV\n")


def main():
    if "--checks" in sys.argv:
        checks()

    print("Table tab:He3Spike -- optimum of G = P_fus/P_brem over temperature\n")
    print("     x   Z_eff   T_opt[keV]   G_max   G_max/G_max(0)"
          "   f_n primary   f_n full burn")
    rows = [(x,) + optimum(x) + (optimum(x, full=True)[2],)
            for x in (0.0, 0.05, 0.10, 0.20, 0.35, 0.50)]
    G0 = rows[0][2]
    for x, Topt, Gmax, fn, fn_full in rows:
        print("  %4.2f   %5.2f   %8.0f   %5.2f   %12.1f   %11.2f   %13.2f"
              % (x, zeff(x), Topt, Gmax, Gmax / G0, fn, fn_full))

    xs = np.linspace(0.0, 0.9, 901)
    Gx = np.array([gain(x).max() for x in xs])
    k = int(np.argmax(Gx))
    print("\nGlobal optimum (primary reactions): G = %.2f at x = %.2f, T = %.0f keV"
          % (Gx[k], xs[k], optimum(xs[k])[0]))
    span = Gx[k] - Gx[0]
    for xq in (0.05, 0.10, 0.20):
        j = int(np.argmin(abs(xs - xq)))
        print("  x = %4.2f captures %4.1f%% of the attainable gain"
              % (xq, 100.0 * (Gx[j] - Gx[0]) / span))

    Gxf = np.array([gain(x, full=True).max() for x in xs])
    kf = int(np.argmax(Gxf))
    print("\nStrong burn-up limit: pure dd reaches G = %.2f; best mixture"
          " G = %.2f at x = %.2f, T = %.0f keV"
          % (Gxf[0], Gxf[kf], xs[kf], optimum(xs[kf], full=True)[0]))

    print("\nNeutron burden [neutrons per MJ of charged-particle heating]"
          " at T = 116 keV")
    i = int(np.argmin(abs(T - 116.0)))
    for x in (0.0, 0.05, 0.10, 0.20, 0.50):
        p = powers(x, slice(i, i + 1))
        print("  x = %4.2f:  primary %.2e,  full burn %.2e"
              % (x, p["Rddn"][0] / p["P_ch"][0] * 1e6,
                 (p["Rddn"][0] + p["Rddp"][0]) / p["P_ch_full"][0] * 1e6))
    Rdt = 0.25 * SV_DT
    j = int(np.argmax(Rdt * ECH_DT * MEV_J / brem(T, 0.0)))
    print("  equimolar dt at its own optimum (T = %.0f keV): %.2e"
          % (T[j], Rdt[j] / (Rdt[j] * ECH_DT * MEV_J) * 1e6))

    print("\nTemperature at which d+3He charged heating overtakes dd")
    for x in (0.05, 0.10, 0.50):
        p = powers(x)
        r = (p["Rd3"] * ECH_D3) / (p["Rddp"] * ECH_DDP + p["Rddn"] * ECH_DDN)
        print("  x = %4.2f:  T = %.0f keV" % (x, T[int(np.argmin(abs(r - 1.0)))]))


if __name__ == "__main__":
    main()
