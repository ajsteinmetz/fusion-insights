#!/usr/bin/env python3
"""Bosch-Hale peak cross-sections for the d+d, t+d and d+3He curves of Fig. 'InteractionLength'.

Source
------
H.-S. Bosch and G. M. Hale, "Improved formulas for fusion cross-sections and
thermal reactivities", Nucl. Fusion 32, 611 (1992).  doi:10.1088/0029-5515/32/4/I07

    sigma(E) = S(E) / ( E exp(B_G / sqrt(E)) )                      [mb]
    S(E)     = (A1 + E(A2 + E(A3 + E(A4 + E A5))))
             / ( 1 + E(B1 + E(B2 + E(B3 + E B4))) )                 [keV mb]

E is the CENTRE-OF-MASS energy in keV.  (Verified: the T(d,n) set below peaks at
5.07 b at E_cm = 64.8 keV, the canonical D-T value; the lab deuteron energy is
E_lab = E_cm (m_d+m_t)/m_t = 108 keV.)

Only the low-energy coefficient sets are kept.  Each one brackets the peak of
its channel, so the high-energy sets are not needed here.

Usage
-----
    python bosch_hale.py            # peak of each channel + the d+d sum
    python bosch_hale.py --table    # sigma(E) and S(E) for d+d vs energy
"""
import math
import sys

# name: (B_G [sqrt(keV)], [A1..A5], [B1..B4], (Emin, Emax) [keV c.m.])
REACTIONS = {
    "T(d,n)4He": (34.3827,
                  [6.927e4, 7.454e8, 2.050e6, 5.2002e4, 0.0],
                  [6.38e1, -9.95e-1, 6.981e-5, 1.728e-4], (0.5, 550)),
    "3He(d,p)4He": (68.7508,
                    [5.7501e6, 2.5226e3, 4.5566e1, 0.0, 0.0],
                    [-3.1995e-3, -8.5530e-6, 5.9014e-8, 0.0], (0.3, 900)),
    "D(d,p)T": (31.3970,
                [5.5576e4, 2.1054e2, -3.2638e-2, 1.4987e-6, 1.8181e-10],
                [0.0, 0.0, 0.0, 0.0], (0.5, 5000)),
    "D(d,n)3He": (31.3970,
                  [5.3701e4, 3.3027e2, -1.2706e-1, 2.9327e-5, -2.5151e-9],
                  [0.0, 0.0, 0.0, 0.0], (0.5, 4900)),
}

# target mass number and E_lab/E_cm ratio (projectile on stationary target)
LAB = {"T(d,n)4He": ("t on D", 2, 5.0 / 2.0),
       "3He(d,p)4He": ("d on 3He", 3, 5.0 / 3.0),
       "D(d,p)T": ("d on D", 2, 2.0),
       "D(d,n)3He": ("d on D", 2, 2.0)}


def s_factor(name, E):
    """Astrophysical S-factor in keV*mb at c.m. energy E [keV]."""
    _, A, B, _ = REACTIONS[name]
    num = A[0] + E * (A[1] + E * (A[2] + E * (A[3] + E * A[4])))
    den = 1.0 + E * (B[0] + E * (B[1] + E * (B[2] + E * B[3])))
    return num / den


def sigma_mb(name, E):
    """Cross-section in mb at c.m. energy E [keV]."""
    BG = REACTIONS[name][0]
    return s_factor(name, E) / (E * math.exp(BG / math.sqrt(E)))


def scan(fn, lo, hi, n=200000):
    """Return (max value, argmax) of fn on [lo, hi]."""
    best = (0.0, lo)
    for i in range(n + 1):
        E = lo + (hi - lo) * i / n
        if E <= 0:
            continue
        v = fn(E)
        if v > best[0]:
            best = (v, E)
    return best


def areal_mass(A_target, sigma_barn):
    """m_areal = A/(N_A sigma) in g/cm^2; the constant is 1 u in grams."""
    return 1.66054 * A_target / sigma_barn


def main():
    if "--table" in sys.argv:
        print("d + d summed over both branches (Bosch-Hale)\n")
        print("  E_cm[keV]  s(d,p)t[mb]  s(d,n)3He[mb]   sum[mb]   S(d,p)[keV b]")
        for E in (5, 10, 25, 50, 100, 200, 500, 1000, 1294, 2000, 3000, 4000):
            a = sigma_mb("D(d,p)T", E)
            b = sigma_mb("D(d,n)3He", E)
            S = s_factor("D(d,p)T", E) / 1000.0
            print("  %8d   %10.4f   %12.4f  %8.2f   %12.1f" % (E, a, b, a + b, S))
        return

    print("Peak cross-sections (Bosch-Hale 1992)\n")
    for nm, (BG, A, B, (lo, hi)) in REACTIONS.items():
        s, E = scan(lambda E, nm=nm: sigma_mb(nm, E), lo, hi)
        beam, At, r = LAB[nm]
        print("  %-12s  sigma = %6.3f b  at E_cm = %7.1f keV "
              "(E_lab = %7.1f keV, %s)" % (nm, s / 1000, E, E * r, beam))

    tot, E = scan(lambda E: sigma_mb("D(d,p)T", E) + sigma_mb("D(d,n)3He", E),
                  0.5, 4900)
    print("\n  d + d SUM     sigma = %6.3f b  at E_cm = %7.1f keV "
          "(E_lab = %7.1f keV, d on D)" % (tot / 1000, E, 2 * E))

    print("\nValues adopted in NucInterL.tex\n")
    print("  channel     sigma[b]  E_cm[MeV]  m_areal[g/cm^2]")
    for label, sig, Ecm, At in (("d + d", 0.19, 1.25, 2),
                                ("t + d", 5.07, 0.065, 2),
                                ("d + 3He", 0.82, 0.26, 3)):
        print("  %-10s  %7.2f  %8.3f  %14.4f"
              % (label, sig, Ecm, areal_mass(At, sig)))


if __name__ == "__main__":
    main()
