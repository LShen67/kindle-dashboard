#!/usr/bin/env python3
"""Render a weather dashboard PNG for a Kindle Paperwhite 3 (1072x1448, grayscale)."""
import json
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont

# --- Settings -------------------------------------------------------------
PLACE = "Westminster, London"
LAT, LON = 51.4975, -0.1357
TZ = "Europe/London"
WIDTH, HEIGHT = 1072, 1448  # Paperwhite 3 portrait
OUT = "dashboard.png"
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
# ---------------------------------------------------------------------------

API = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}&timezone={TZ.replace('/', '%2F')}"
    "&current=temperature_2m,apparent_temperature,weather_code,wind_speed_10m,relative_humidity_2m"
    "&hourly=temperature_2m,precipitation_probability,weather_code"
    "&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset"
    "&wind_speed_unit=mph&forecast_days=4"
)

# WMO weather codes, as documented by Open-Meteo
WMO = {
    0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 48: "Freezing fog",
    51: "Light drizzle", 53: "Drizzle", 55: "Heavy drizzle",
    56: "Freezing drizzle", 57: "Freezing drizzle",
    61: "Light rain", 63: "Rain", 65: "Heavy rain",
    66: "Freezing rain", 67: "Freezing rain",
    71: "Light snow", 73: "Snow", 75: "Heavy snow", 77: "Snow grains",
    80: "Light showers", 81: "Showers", 82: "Heavy showers",
    85: "Snow showers", 86: "Snow showers",
    95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm",
}


def font(size, bold=False):
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(FONT_DIR + name, size)


def fetch():
    with urllib.request.urlopen(API, timeout=30) as r:
        data = json.load(r)
    if data.get("error"):
        raise RuntimeError(data.get("reason"))
    return data


def sample():
    """Offline example data, used with --sample for testing the layout."""
    now = datetime.now(ZoneInfo(TZ)).replace(minute=0, second=0, microsecond=0)
    hours = [now.replace(hour=h).strftime("%Y-%m-%dT%H:00") for h in range(24)]
    days = [(now.date().fromordinal(now.date().toordinal() + i)).isoformat() for i in range(4)]
    return {
        "current": {"temperature_2m": 8.4, "apparent_temperature": 5.9, "weather_code": 3,
                    "wind_speed_10m": 11.2, "relative_humidity_2m": 81},
        "hourly": {"time": hours,
                   "temperature_2m": [6 + (h % 12) * 0.4 for h in range(24)],
                   "precipitation_probability": [(h * 7) % 60 for h in range(24)],
                   "weather_code": [3] * 24},
        "daily": {"time": days, "weather_code": [3, 61, 2, 80],
                  "temperature_2m_max": [10, 9, 11, 8], "temperature_2m_min": [4, 5, 3, 2],
                  "precipitation_probability_max": [20, 70, 10, 55],
                  "sunrise": [d + "T07:31" for d in days], "sunset": [d + "T16:01" for d in days]},
    }


def render(w, out=OUT):
    img = Image.new("L", (WIDTH, HEIGHT), 255)  # 8-bit grayscale, no alpha
    d = ImageDraw.Draw(img)
    now = datetime.now(ZoneInfo(TZ))
    M = 64  # outer margin
    cur, daily, hourly = w["current"], w["daily"], w["hourly"]

    # Header
    d.text((M, 56), now.strftime("%A %-d %B"), font=font(56, True), fill=0)
    d.text((M, 128), PLACE, font=font(34), fill=80)
    d.line((M, 196, WIDTH - M, 196), fill=0, width=3)

    # Now
    d.text((M, 230), f"{round(cur['temperature_2m'])}°", font=font(220, True), fill=0)
    x = 560
    d.text((x, 260), WMO.get(cur["weather_code"], "—"), font=font(52, True), fill=0)
    d.text((x, 340), f"Feels like {round(cur['apparent_temperature'])}°", font=font(38), fill=40)
    d.text((x, 395), f"Wind {round(cur['wind_speed_10m'])} mph", font=font(38), fill=40)
    d.text((x, 450), f"Humidity {cur['relative_humidity_2m']}%", font=font(38), fill=40)
    sr, ss = daily["sunrise"][0][11:16], daily["sunset"][0][11:16]
    d.text((M, 520), f"Today {round(daily['temperature_2m_min'][0])}° – {round(daily['temperature_2m_max'][0])}°"
                     f"   ·   Sunrise {sr}   Sunset {ss}", font=font(32), fill=40)
    d.line((M, 590, WIDTH - M, 590), fill=0, width=3)

    # Next hours (from the current hour, every 2 hours, 6 columns)
    d.text((M, 615), "NEXT HOURS", font=font(28, True), fill=80)
    times = hourly["time"]
    key = now.strftime("%Y-%m-%dT%H:00")
    start = times.index(key) if key in times else 0
    idx = [start + i * 2 for i in range(6) if start + i * 2 < len(times)]
    col = (WIDTH - 2 * M) / 6
    for n, i in enumerate(idx):
        cx = M + col * n + col / 2
        for text, y, f, fill in (
            (times[i][11:16], 670, font(32), 60),
            (f"{round(hourly['temperature_2m'][i])}°", 715, font(52, True), 0),
            (f"{hourly['precipitation_probability'][i] or 0}%", 785, font(30), 60),
        ):
            d.text((cx, y), text, font=f, fill=fill, anchor="ma")
    d.text((M, 830), "Percent = chance of rain", font=font(24), fill=120)
    d.line((M, 880, WIDTH - M, 880), fill=0, width=3)

    # Next days
    d.text((M, 905), "NEXT DAYS", font=font(28, True), fill=80)
    y = 955
    for i in range(1, min(4, len(daily["time"]))):
        day = datetime.fromisoformat(daily["time"][i]).strftime("%A")
        d.text((M, y), day, font=font(42, True), fill=0)
        d.text((M + 300, y + 4), WMO.get(daily["weather_code"][i], "—"), font=font(36), fill=40)
        d.text((WIDTH - M, y), f"{round(daily['temperature_2m_min'][i])}° / {round(daily['temperature_2m_max'][i])}°",
               font=font(42, True), fill=0, anchor="ra")
        d.text((WIDTH - M, y + 52), f"Rain {daily['precipitation_probability_max'][i] or 0}%",
               font=font(28), fill=80, anchor="ra")
        y += 110
    d.line((M, 1290, WIDTH - M, 1290), fill=0, width=3)

    # Footer (to-do list will go above this later)
    d.text((M, 1320), f"Updated {now.strftime('%H:%M')}", font=font(28), fill=80)
    d.text((WIDTH - M, 1320), "Weather data by Open-Meteo.com", font=font(24), fill=120, anchor="ra")

    img.save(out, optimize=True)
    print(f"Saved {out}")


if __name__ == "__main__":
    render(sample() if "--sample" in sys.argv else fetch())
