
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nacre_reactivity as nr

# -----------------------------
# Configuration
# -----------------------------
# Default local CSV (override via CLI or by editing here)
CSV_PATH = "C:/Users/astei/Source/Repos/aneutronic-fusion/_python/nacre_pb.csv"  # NACRE II table with columns: T9, adopted, low, high

# Temperature grid (1–1000 keV)
T_keV = np.logspace(0, 3, 400)

# p + 11B -> 3α   (Q ≈ 8.68 MeV; essentially all to α's)
Q_ALPHA_J = 8.68 * nr.MEV_TO_J

# Mixture: equal ion densities n_p = n_B (r = n_p/n_B = 1), charges Z_p=1, Z_B=5
C_pB    = nr.composition_coeff(ZA=1, ZB=5, r=1.0)   # = 1/36
Zeff_pB = nr.zeff(ZA=1, ZB=5, r=1.0)                # = 13/3

def load_all_rates(csv_path):
    """Return dict of NacreRate objects for 'adopted', 'low', 'high'."""
    rates = {}
    for which in ("adopted", "low", "high"):
        rates[which] = nr.load_nacre_rates(csv_path, which=which)
    return rates

def compute_curves(rates, T_keV):
    """Compute reactivity and power curves for each rate choice."""
    out = {}
    for which, rate in rates.items():
        sv = rate.sigmav_keV(T_keV)  # m^3/s
        Palpha = nr.power_per_ne2(T_keV, sv, Q_Joule=Q_ALPHA_J, C=C_pB)
        out[which] = {"sv": sv, "Palpha": Palpha}
    # Bremsstrahlung depends only on Zeff and T, not on the reactivity choice
    Pbrem = nr.brem_per_ne2(T_keV, Z_eff=Zeff_pB)
    return out, Pbrem

def save_csvs(T_keV, curves, Pbrem):
    # Combined CSV (reactivity + power)
    df = pd.DataFrame({
        "T_keV": T_keV,
        "sv_m3_per_s_adopted": curves["adopted"]["sv"],
        "sv_m3_per_s_low":      curves["low"]["sv"],
        "sv_m3_per_s_high":     curves["high"]["sv"],
        "Palpha_per_ne2_Wm3_adopted": curves["adopted"]["Palpha"],
        "Palpha_per_ne2_Wm3_low":      curves["low"]["Palpha"],
        "Palpha_per_ne2_Wm3_high":     curves["high"]["Palpha"],
        "Pbrem_per_ne2_Wm3": Pbrem,
    })
    df.to_csv("pb_curves_for_tikz.csv", index=False)

    # Reactivity-only CSV
    df_reac = pd.DataFrame({
        "T_keV": T_keV,
        "sv_m3_per_s_adopted": curves["adopted"]["sv"],
        "sv_m3_per_s_low":      curves["low"]["sv"],
        "sv_m3_per_s_high":     curves["high"]["sv"],
    })
    df_reac.to_csv("pb_reactivity_for_tikz.csv", index=False)

def main():
    rates = load_all_rates(CSV_PATH)
    curves, Pbrem = compute_curves(rates, T_keV)
    save_csvs(T_keV, curves, Pbrem)
    print("Wrote: pb_curves_for_tikz.csv and pb_reactivity_for_tikz.csv")

if __name__ == "__main__":
    main()
