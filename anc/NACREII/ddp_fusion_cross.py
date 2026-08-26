import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nacre_reactivity as nr

# -----------------------------
# Configuration
# -----------------------------
# Default local CSV (override by editing or passing via import)
CSV_PATH = "C:/Users/astei/Source/Repos/aneutronic-fusion/_python/nacre_ddp.csv"  # NACRE II (Table 5): T9, adopted, low, high

# Temperature grid (1–1000 keV)
T_keV = np.logspace(0, 3, 400)

# DD (p) energetics: D(d,p)T — charged energy available for direct heating ~ 3.02 MeV carried by proton
Q_CHARGED_J = 3.02 * nr.MEV_TO_J

# Composition: pure deuterium (self-collisions), r = n_D/n_D = 1, Z_D = 1
C_DD   = nr.composition_coeff(ZA=1, ZB=1, r=1.0)   # = 1/4
Zeff_D = nr.zeff(ZA=1, ZB=1, r=1.0)                # = 1.0

def load_all_rates(csv_path):
    """Return dict of NacreRate objects for 'adopted', 'low', 'high'."""
    return {which: nr.load_nacre_rates(csv_path, which=which)
            for which in ("adopted", "low", "high")}

def compute_curves(rates, T_keV):
    """Compute ⟨σv⟩ and charged-particle heating per n_e^2 for each rate set."""
    out = {}
    for which, rate in rates.items():
        sv = rate.sigmav_keV(T_keV)  # m^3/s
        Pchg = nr.power_per_ne2(T_keV, sv, Q_Joule=Q_CHARGED_J, C=C_DD)
        out[which] = {"sv": sv, "Pchg": Pchg}
    Pbrem = nr.brem_per_ne2(T_keV, Z_eff=Zeff_D)
    return out, Pbrem

def save_csvs(T_keV, curves, Pbrem):
    # Combined CSV (reactivity + power)
    df = pd.DataFrame({
        "T_keV": T_keV,
        "sv_m3_per_s_adopted": curves["adopted"]["sv"],
        "sv_m3_per_s_low":      curves["low"]["sv"],
        "sv_m3_per_s_high":     curves["high"]["sv"],
        "Pchg_per_ne2_Wm3_adopted": curves["adopted"]["Pchg"],
        "Pchg_per_ne2_Wm3_low":      curves["low"]["Pchg"],
        "Pchg_per_ne2_Wm3_high":     curves["high"]["Pchg"],
        "Pbrem_per_ne2_Wm3": Pbrem,
    })
    df.to_csv("ddp_curves_for_tikz.csv", index=False)

    # Reactivity-only CSV
    df_reac = pd.DataFrame({
        "T_keV": T_keV,
        "sv_m3_per_s_adopted": curves["adopted"]["sv"],
        "sv_m3_per_s_low":      curves["low"]["sv"],
        "sv_m3_per_s_high":     curves["high"]["sv"],
    })
    df_reac.to_csv("ddp_reactivity_for_tikz.csv", index=False)

def main():
    rates = load_all_rates(CSV_PATH)
    curves, Pbrem = compute_curves(rates, T_keV)
    save_csvs(T_keV, curves, Pbrem)
    print("Wrote: ddp_curves_for_tikz.csv and ddp_reactivity_for_tikz.csv")

if __name__ == "__main__":
    main()
