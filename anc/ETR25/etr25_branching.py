
"""
etr25_branching.py — CNO-II/CNO-III branching at the 17O node.

Computes the ratio of thermal reaction rates

    R_17 = <sigma v>[17O(p,g)18F] / <sigma v>[17O(p,a)14N]

and the fraction of reacting 17O leaking into the CNO-III sequence,

    f_pg = R_17 / (1 + R_17),

from the ETR25 median rates tabulated in etr25_17op_g.csv and
etr25_17op_a.csv. Reproduces the numbers quoted in the CNO section of the
manuscript at the solar core temperature T9 = 0.015.

The CSVs use the same T9,adopted,low,high layout as the NACRE II tables, so
they are read with anc/NACREII/nacre_reactivity.py.
"""

import os
import sys

import numpy as np

# Reuse the NACRE II loader/interpolator (same CSV layout).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "NACREII"))
import nacre_reactivity as nr

# -----------------------------
# Configuration
# -----------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PG = os.path.join(HERE, "etr25_17op_g.csv")  # ETR25 Table 23: 17O(p,g)18F
CSV_PA = os.path.join(HERE, "etr25_17op_a.csv")  # ETR25 Table 24: 17O(p,a)14N

# Solar core temperature, T_sun ~ 1.5e7 K
T9_SOLAR = 0.015


def branching(T9, which="adopted"):
    """Return (R_17, f_pg) at temperature T9 for the given rate percentile."""
    pg = nr.load_nacre_rates(CSV_PG, which=which)
    pa = nr.load_nacre_rates(CSV_PA, which=which)
    R = pg.NA_sigmav_T9(T9) / pa.NA_sigmav_T9(T9)
    return R, R / (1.0 + R)


def factor_uncertainty(csv_path, T9):
    """Return the ETR25 factor uncertainty f.u. tabulated at T9."""
    import pandas as pd
    df = pd.read_csv(csv_path)
    return float(df.loc[np.isclose(df["T9"], T9), "fu"].iloc[0])


def main():
    T9 = float(sys.argv[1]) if len(sys.argv) > 1 else T9_SOLAR

    pg = nr.load_nacre_rates(CSV_PG)
    pa = nr.load_nacre_rates(CSV_PA)
    print(f"ETR25 median rates at T9 = {T9:g} "
          f"(N_A<sigma v>, cm^3 mol^-1 s^-1):")
    print(f"  17O(p,g)18F : {pg.NA_sigmav_T9(T9):.4g}"
          f"   f.u. = {factor_uncertainty(CSV_PG, T9):.3g}")
    print(f"  17O(p,a)14N : {pa.NA_sigmav_T9(T9):.4g}"
          f"   f.u. = {factor_uncertainty(CSV_PA, T9):.3g}")

    R, f = branching(T9)
    print(f"\n  R_17 = <sv>_pg / <sv>_pa = {R:.4f}")
    print(f"  f_pg = R_17 / (1 + R_17)  = {f:.4f}  "
          f"-> {100 * f:.0f}% into CNO-III, {100 * (1 - f):.0f}% back to CNO-I")


if __name__ == "__main__":
    main()
