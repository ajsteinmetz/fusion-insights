#!/usr/bin/env python3
"""Peak cross-sections from the EXFOR files fetched by fetch_exfor.sh.

For every measurement it prints the maximum of the excitation function and the
lab energy at which it occurs, grouped by channel, so the values adopted in
NucInterL.tex can be traced back to individual datasets and the spread between
discrepant measurements can be judged.

Usage:  python exfor_peaks.py [cache_dir] [--emax MeV] [--adopted]

File format (exfortables / YANDF-0.4): '#'-comment header carrying the EXFOR
reaction string and subentry, then columns  E[MeV]  dE  xs[mb]  dxs  norm.
"""
import glob
import os
import sys

# Values adopted in NucInterL.tex, with the dataset each comes from.
ADOPTED = [
    ("p + 6Li", 0.22, 1.54, 1.80, 6,
     "6Li(p,3He)4He 217 mb @ E_p=1.78 MeV; Elwyn 1979 (F0012005). "
     "Spread 184-280 mb across Elwyn/ChiaShouLin/Marion/Hooton."),
    ("p + 7Li", 0.09, 2.63, 3.00, 7,
     "7Li(p,a)4He 86 mb @ E_p=3.0 MeV; Cassagnou 1962 (A1475005). "
     "Mani 1964 gives 131 mb at the same energy. "
     "7Li(p,n)7Be excluded: Q=-1.64 MeV (endothermic), peaks at 0.58 b."),
    ("p + 9Be", 0.83, 0.30, 0.33, 9,
     "9Be(p,a)6Li 0.36 b + 9Be(p,d)8Be 0.47 b @ E_p=0.33 MeV; "
     "Sierk & Tombrello 1973 (F0169004/5), confirmed by Zahnow 1997."),
    ("p + 11B", 1.22, 0.60, 0.655, 11,
     "11B(p,a1)8Be* 1.22 b @ E_p=0.655 MeV; Becker 1987 (A0413005). "
     "(p,a0) adds <10 mb there."),
    ("d + 6Li", 0.44, 0.75, 1.00, 6,
     "@ E_d=1.0 MeV: (d,a) 0.057 (Bertrand) + (d,p0+p1) 0.094 (Mcclenahan) "
     "+ (d,n)7Be 0.099 (Ruby) + (d,t)5Li 0.188 (Macklin). "
     "Softest number in the set; channels disagree by up to 2x between groups."),
    ("d + 7Li", 0.60, 0.78, 1.00, 7,
     "Total exothermic yield ~0.55-0.7 b @ E_d=1.0 MeV, from neutron "
     "production (Bochkarev 1994, A0551003); dominated by (d,n)8Be and "
     "(d,n a)a. (d,p)8Li (Q=-0.19) and (d,t)6Li (Q=-0.99) excluded."),
]


def read(fn):
    """Return (EXFOR reaction string, [(E[MeV], xs[mb]), ...])."""
    react, pts = "", []
    with open(fn, errors="ignore") as fh:
        for line in fh:
            if line.startswith("#"):
                if "X4 reaction" in line:
                    react = line.split(":", 1)[1].strip()
                continue
            c = line.split()
            if len(c) >= 4:
                try:
                    pts.append((float(c[0]), float(c[2])))
                except ValueError:
                    pass
    return react, pts


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cache = args[0] if args else "./exfor-cache"
    emax = 6.0
    if "--emax" in sys.argv:
        emax = float(sys.argv[sys.argv.index("--emax") + 1])

    if "--adopted" in sys.argv:
        print("Adopted in NucInterL.tex   (m_areal = 1.66054 A / sigma)\n")
        for lbl, sig, ecm, elab, At in ((a[0], a[1], a[2], a[3], a[4]) for a in ADOPTED):
            print("  %-9s sigma=%5.2f b  E_cm=%5.2f MeV  E_lab=%5.2f MeV  "
                  "m_areal=%7.3f g/cm2" % (lbl, sig, ecm, elab, 1.66054 * At / sig))
        print()
        for a in ADOPTED:
            print("  %-9s %s" % (a[0], a[5]))
        return

    dirs = sorted(d for d in glob.glob(os.path.join(cache, "*", "*", "xs", "*"))
                  if os.path.isdir(d))
    if not dirs:
        sys.exit("no data under %s -- run fetch_exfor.sh first" % cache)

    for d in dirs:
        rel = os.path.relpath(d, cache).replace("\\", "/")
        print("\n===== " + rel)
        for fn in sorted(glob.glob(os.path.join(d, "*"))):
            react, pts = read(fn)
            sel = [p for p in pts if p[0] <= emax]
            if not sel:
                continue
            E, xs = max(sel, key=lambda t: t[1])
            print("  %-52s n=%3d  E=[%.3f,%.3f]  max %8.1f mb at %.3f MeV  %s"
                  % (os.path.basename(fn), len(pts), pts[0][0], pts[-1][0],
                     xs, E, react))


if __name__ == "__main__":
    main()
