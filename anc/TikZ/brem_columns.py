#!/usr/bin/env python3
"""Recompute the bremsstrahlung columns of the power-balance figure data.

The PowerInRadOut* figures (Figs. 8-10 of the manuscript) plot P_brem/n_e^2
from these CSV files.  Their bremsstrahlung columns were generated with an
effective prefactor 4.83e-37 x 1.328 W m^3 keV^-1/2, i.e. the NRL Formulary
constant (5.35e-37, which already contains the averaged Gaunt factor) times a
second Gaunt factor of about 1.2.  This script rewrites them with Eq.
(eq:powerBrem) of the manuscript, the same expression used for table
'tab:He3Spike' in ../EXFOR/he3_spike_optimum.py:

    P_brem/n_e^2 = C_b Z_eff sqrt(T) (1 + a_1 T / m_e c^2) g_B ,  T in keV,

with C_b = 4.83e-37 W m^3 keV^-1/2, g_B = 1.1, a_1 = 2.6, m_e c^2 = 511 keV,
so C_b g_B = 5.31e-37, matching the NRL value.  At fixed electron density a
3He number fraction x = n_3/(n_d + n_3) gives Z_eff = (1 + 3x)/(1 + x).

Only the Pbrem columns change; every other column, the header, the row order
and the line endings are kept.  See issue #54.

Usage (from anywhere):  python anc/TikZ/brem_columns.py
"""
import os
import re

CB, GB, A1, MEC2 = 4.83e-37, 1.1, 2.6, 511.0      # Eq.(eq:powerBrem)

HERE = os.path.dirname(os.path.abspath(__file__))

# file -> {column: 3He number fraction x}
FILES = {
    'd3he_power_brem_curves_for_tikz.csv': {
        'Pbrem_per_ne2_pureD_x0_Wm3': 0.0,
        'Pbrem_per_ne2_He3_5pct_x0p05_Wm3': 0.05,
        'Pbrem_per_ne2_He3_10pct_x0p1_Wm3': 0.10,
        'Pbrem_per_ne2_He3_50pct_x0p5_Wm3': 0.50,
    },
    'dt_curves_for_tikz.csv': {'Pbrem_per_ne2_Wm3': 0.0},                    # hydrogenic, Z_eff = 1
    'dt_fully_boosted_with_dd_he3_for_tikz.csv': {'Pbrem_per_ne2_Wm3': 0.0},
}


def zeff(x):
    return (1.0 + 3.0 * x) / (1.0 + x)


def brem(T, x):
    """P_brem / n_e^2 [W m^3] at temperature T [keV], Eq.(eq:powerBrem)."""
    return CB * zeff(x) * T**0.5 * (1.0 + A1 * T / MEC2) * GB


def rewrite(name, columns):
    path = os.path.join(HERE, name)
    with open(path, newline='') as f:
        lines = f.read().splitlines(keepends=True)
    header = lines[0].rstrip('\r\n').split(',')
    iT = header.index('T_keV')
    idx = {header.index(c): x for c, x in columns.items()}
    out = [lines[0]]
    for line in lines[1:]:
        body = line.rstrip('\r\n')
        if not body:
            out.append(line)
            continue
        eol = line[len(body):]
        cells = body.split(',')
        T = float(cells[iT])
        for i, x in idx.items():
            cells[i] = repr(brem(T, x))
        out.append(','.join(cells) + eol)
    with open(path, 'w', newline='') as f:
        f.write(''.join(out))
    print('%s: %d rows, columns %s' % (name, len(out) - 1, ', '.join(columns)))


if __name__ == '__main__':
    for name, columns in FILES.items():
        rewrite(name, columns)
