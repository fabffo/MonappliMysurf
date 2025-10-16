# api_scoreplage.py
from fastapi import FastAPI, Query
from fastapi.responses import PlainTextResponse
import json, math, urllib.request

app = FastAPI(title="Surf Score API testb(plain text)")

# ---------- Utils ----------
def scale(value, in_min, in_max, out_min=0.0, out_max=1.0):
    if value is None: return None
    v = max(min(value, in_max), in_min)
    r = (v - in_min) / (in_max - in_min) if in_max != in_min else 0.0
    return out_min + r * (out_max - out_min)

def mean(vals):
    vs = [v for v in vals if v is not None]
    return sum(vs) / len(vs) if vs else None

def deg_to_rad(d):
    return (d * math.pi) / 180.0

def directional_affinity(spot_deg, swell_deg):
    if spot_deg is None or swell_deg is None: return 0.5
    diff = abs(((swell_deg - spot_deg + 540) % 360) - 180)
    return max(0.0, math.cos(deg_to_rad(diff)))

def orient_label(score):
    if score is None: return "indéterminé"
    if score >= 0.7: return "bon alignement"
    if score >= 0.4: return "alignement moyen"
    return "mauvais alignement"

def tide_score_from_height(pref, h, low_max, high_min, high_max, full_span):
    if h is None: return None
    if pref == "low":  # plus c'est bas, mieux c'est
        return scale(h, 0.0, low_max, 1.0, 0.0)
    if pref == "high": # plus c'est haut, mieux c'est
        return scale(h, high_min, high_max, 0.0, 1.0)
    # 'mid': pic vers le milieu de [0..full_span]
    mid_scaled = scale(h, 0.0, full_span, 0.0, 1.0)
    if mid_scaled is None: return None
    return max(0.0, 1.0 - abs(mid_scaled - 0.5) * 2.0)

def tide_band_from_height(h, low_max, high_min, high_max):
    if h is None: return "inconnue"
    if h <= low_max: return "low"
    if high_min <= h <= high_max:
        return "high" if h >= (high_min + high_max)/2 else "mid"
    return "high" if h > high_max else "mid"

def fetch_openmeteo_first_hour(lat, lon, tz="Europe/Paris"):
    url = (
        "https://marine-api.open-meteo.com/v1/marine"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=wave_height,wave_period,wave_direction,sea_surface_temperature,"
        "sea_level_height_msl,ocean_current_velocity,ocean_current_direction"
        f"&timezone={tz}&forecast_days=1"
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
    }

# ---------- Endpoint: texte brut ----------
@app.get("/score", response_class=PlainTextResponse)
def score(
    # Biarritz par défaut
    lat: float = Query(43.483),
    lon: float = Query(-1.558),
    spot_orientation_deg: float = Query(300, description="Orientation du spot (ex: 300 = NW)"),
    tide_pref: str = Query("mid", pattern="^(low|mid|high)$"),
    # Plage idéale (range)
    ideal_height_min: float = Query(0.8),
    ideal_height_max: float = Query(2.2),
    ideal_period_min: float = Query(8.0),
    ideal_period_max: float = Query(14.0),
    # Poids
    w_range: float = Query(0.60),
    w_orient: float = Query(0.25),
    w_tide: float = Query(0.15),
    # Param marée (proxy hauteur relative)
    tide_low_max: float = Query(0.8),
    tide_high_min: float = Query(0.8),
    tide_high_max: float = Query(1.8),
    tide_full_span: float = Query(1.6),
    timezone: str = Query("Europe/Paris"),
):
    first = fetch_openmeteo_first_hour(lat, lon, tz=timezone)

    # sous-scores
    height_score = scale(first["wave_height_m"], ideal_height_min, ideal_height_max)
    period_score = scale(first["wave_period_s"], ideal_period_min, ideal_period_max)
    range_score = mean([height_score, period_score])

    orient_score = directional_affinity(spot_orientation_deg, first["wave_direction_deg"])
    tide_score = tide_score_from_height(tide_pref, first["sea_level_msl_m"], tide_low_max, tide_high_min, tide_high_max, tide_full_span)

    parts, used = [], 0.0
    for val, w in [(range_score, w_range), (orient_score, w_orient), (tide_score, w_tide)]:
        if val is not None:
            parts.append(val * w); used += w
    note = round((sum(parts) / used) * 100) if parts else None

    # labels
    orient_txt = orient_label(orient_score)
    tide_band  = tide_band_from_height(first["sea_level_msl_m"], tide_low_max, tide_high_min, tide_high_max)

    # texte EXACT au format demandé
    note_line = (
        f"NOTE = {note}/100  (poids: plage={w_range}, orientation={w_orient}, marée={w_tide})"
        if note is not None else
        "NOTE = N/A (données insuffisantes)"
    )

    text = (
        "=== Conditions idéales (profil spot) ===\n"
        f"• Plage (houle) idéale : hauteur {ideal_height_min}–{ideal_height_max} m, période {ideal_period_min}–{ideal_period_max} s\n"
        f"• Orientation idéale   : spot ~{int(spot_orientation_deg)}° (NW)\n"
        f"• Marée idéale         : {tide_pref}\n\n"
        "=== Conditions actuelles (1re heure dispo) ===\n"
        f"• Heure Europe/Paris   : {first['time']}\n"
        f"• Orientation houle    : {first['wave_direction_deg']}°  → {orient_txt}\n"
        f"• Marée (proxy hauteur): {first['sea_level_msl_m']} m  → bande '{tide_band}' (préférence: {tide_pref})\n"
        f"• Houle mesurée        : {first['wave_height_m']} m @ {first['wave_period_s']} s\n\n"
        "=== Note donnée ===\n"
        f"{note_line}"
    )

    return text

@app.get("/health", response_class=PlainTextResponse)
def health():
    return "ok"
