#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import math
import urllib.request

# ------------------ Config Biarritz (ajuste si besoin) ------------------
LAT = 43.483
LON = -1.558
SPOT_NAME = "Biarritz - Grande Plage"
SPOT_ORIENTATION_DEG = 300           # ~NW ; axe vers lequel le spot "regarde"
TIDE_PREFERENCE = "mid"              # 'low' | 'mid' | 'high'

# "Plage" idéale (au sens range)
IDEAL_SWELL_HEIGHT_M = (0.8, 2.2)    # mètres
IDEAL_SWELL_PERIOD_S = (8.0, 14.0)   # secondes

# Pondérations pour la note (somme 1.0)
WEIGHTS = {"range": 0.60, "orientation": 0.25, "tide": 0.15}

# Pour le proxy marée via hauteur relative (à affiner localement)
TIDE_LOW_MAX_M   = 0.8
TIDE_HIGH_MIN_M  = 0.8
TIDE_HIGH_MAX_M  = 1.8
TIDE_FULL_SPAN_M = 1.6  # pour "mid"

# ------------------ Utilitaires ------------------
def scale(value, in_min, in_max, out_min=0.0, out_max=1.0):
    if value is None:
        return None
    v = max(min(value, in_max), in_min)
    r = (v - in_min) / (in_max - in_min) if in_max != in_min else 0.0
    return out_min + r * (out_max - out_min)

def mean(vals):
    vs = [v for v in vals if v is not None]
    return sum(vs) / len(vs) if vs else None

def deg_to_rad(d):
    return (d * math.pi) / 180.0

def directional_affinity(spot_deg, swell_deg):
    """1 si la houle arrive dans l'axe du spot, 0 si opposée (cosinus sur écart [0..180])."""
    if spot_deg is None or swell_deg is None:
        return 0.5
    diff = abs(((swell_deg - spot_deg + 540) % 360) - 180)  # [0..180]
    return max(0.0, math.cos(deg_to_rad(diff)))

def orient_label(score):
    if score is None:
        return "indéterminé"
    if score >= 0.7:
        return "bon alignement"
    if score >= 0.4:
        return "alignement moyen"
    return "mauvais alignement"

def tide_score_from_height(tide_pref, tide_height_m):
    if tide_height_m is None:
        return None
    if tide_pref == "low":
        return scale(tide_height_m, 0.0, TIDE_LOW_MAX_M, 1.0, 0.0)
    if tide_pref == "high":
        return scale(tide_height_m, TIDE_HIGH_MIN_M, TIDE_HIGH_MAX_M, 0.0, 1.0)
    # "mid": pic vers le milieu de [0..TIDE_FULL_SPAN_M]
    mid_scaled = scale(tide_height_m, 0.0, TIDE_FULL_SPAN_M, 0.0, 1.0)
    if mid_scaled is None:
        return None
    return max(0.0, 1.0 - abs(mid_scaled - 0.5) * 2.0)

def tide_band_from_height(h):
    """Classe 'low' / 'mid' / 'high' sur la base du proxy hauteur relative."""
    if h is None:
        return "inconnue"
    if h <= TIDE_LOW_MAX_M:
        return "low"
    if h >= TIDE_HIGH_MIN_M and h <= TIDE_HIGH_MAX_M:
        # Selon amplitude locale, cette bande peut se recouper; on simplifie:
        return "high" if h >= (TIDE_HIGH_MIN_M + TIDE_HIGH_MAX_M) / 2 else "mid"
    # Hors bornes: approx
    return "high" if h > TIDE_HIGH_MAX_M else "mid"

# ------------------ Fetch Open-Meteo Marine (1re heure) ------------------
def fetch_openmeteo_first_hour(lat, lon):
    url = (
        "https://marine-api.open-meteo.com/v1/marine"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=wave_height,wave_period,wave_direction,sea_surface_temperature,"
        "sea_level_height_msl,ocean_current_velocity,ocean_current_direction"
        "&timezone=Europe%2FParis&forecast_days=1"
    )
    with urllib.request.urlopen(url) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    i = 0
    h = data["hourly"]
    return {
        "time": h["time"][i],
        "wave_height_m": h["wave_height"][i],
        "wave_period_s": h["wave_period"][i],
        "wave_direction_deg": h["wave_direction"][i],
        "sea_surface_temp_c": h["sea_surface_temperature"][i],
        "sea_level_msl_m": h["sea_level_height_msl"][i],
        "current_velocity_ms": h["ocean_current_velocity"][i],
        "current_direction_deg": h["ocean_current_direction"][i],
        "request_url": url,
    }

# ------------------ Calcul note ------------------
def compute_weighted_score(first):
    # "Plage" (range) = adéquation hauteur/période aux plages idéales
    height_score = scale(first["wave_height_m"], IDEAL_SWELL_HEIGHT_M[0], IDEAL_SWELL_HEIGHT_M[1])
    period_score = scale(first["wave_period_s"], IDEAL_SWELL_PERIOD_S[0], IDEAL_SWELL_PERIOD_S[1])
    range_score = mean([height_score, period_score])

    # Orientation houle vs spot
    orient_score = directional_affinity(SPOT_ORIENTATION_DEG, first["wave_direction_deg"])

    # Marée (proxy hauteur relative vs préférence)
    tide_score = tide_score_from_height(TIDE_PREFERENCE, first["sea_level_msl_m"])

    # Agrégation pondérée
    parts, used = [], 0.0
    for key, val in [("range", range_score), ("orientation", orient_score), ("tide", tide_score)]:
        w = WEIGHTS[key]
        if val is not None:
            parts.append(val * w)
            used += w

    if not parts:
        return None, {"range": range_score, "orientation": orient_score, "tide": tide_score}

    score01 = sum(parts) / used if used else 0.0
    return round(score01 * 100), {"range": range_score, "orientation": orient_score, "tide": tide_score}

# ------------------ Sortie demandée ------------------
def main():
    first = fetch_openmeteo_first_hour(LAT, LON)

    note, subs = compute_weighted_score(first)

    # 1) Conditions idéales
    print("=== Conditions idéales (profil spot) ===")
    print(f"• Plage (houle) idéale : hauteur {IDEAL_SWELL_HEIGHT_M[0]}–{IDEAL_SWELL_HEIGHT_M[1]} m, "
          f"période {IDEAL_SWELL_PERIOD_S[0]}–{IDEAL_SWELL_PERIOD_S[1]} s")
    print(f"• Orientation idéale   : spot ~{SPOT_ORIENTATION_DEG}° (NW)")
    print(f"• Marée idéale         : {TIDE_PREFERENCE}")

    # 2) Conditions actuelles (orientation & marée)
    orient_score = subs["orientation"]
    tide_score = subs["tide"]
    orient_txt = orient_label(orient_score)
    tide_band = tide_band_from_height(first["sea_level_msl_m"])

    print("\n=== Conditions actuelles (1re heure dispo) ===")
    print(f"• Heure Europe/Paris   : {first['time']}")
    print(f"• Orientation houle    : {first['wave_direction_deg']}°  → {orient_txt}")
    print(f"• Marée (proxy hauteur): {first['sea_level_msl_m']} m  → bande '{tide_band}' (préférence: {TIDE_PREFERENCE})")

    # (facultatif) Affiche la houle mesurée
    print(f"• Houle mesurée        : {first['wave_height_m']} m @ {first['wave_period_s']} s")

    # 3) Note finale
    print("\n=== Note donnée ===")
    if note is None:
        print("Impossible de calculer la note (données insuffisantes).")
    else:
        print(f"NOTE = {note}/100  (poids: plage={WEIGHTS['range']}, orientation={WEIGHTS['orientation']}, marée={WEIGHTS['tide']})")

if __name__ == "__main__":
    main()
12²A    ZED