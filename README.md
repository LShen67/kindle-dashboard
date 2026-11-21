# Kindle weather dashboard

Turns a jailbroken Kindle Paperwhite 3 (7th gen) into a weather screen for Westminster, London.

How it works:
1. A GitHub Action runs `render.py` every 30 minutes.
2. It gets weather from Open-Meteo and saves `dashboard.png` (1072×1448, grayscale).
3. kindle-dash on the Kindle downloads that picture and shows it.

## Test locally
    pip install pillow
    python render.py --sample   # offline example data
    python render.py            # live weather

## Kindle setup
1. Jailbreak the Kindle (LanguageBreak works up to firmware 5.16.2.1.1).
2. Install USBNetwork for SSH, and set up Wi-Fi.
3. Download kindle-dash: https://github.com/pascalw/kindle-dash/releases
4. Replace its `local/fetch-dashboard.sh` with `kindle/fetch-dashboard.sh` from this repo (edit the URL first).
5. `rsync -vr ./ kindle:/mnt/us/dashboard`, then run `/mnt/us/dashboard/start.sh` on the Kindle.

Weather data by Open-Meteo.com (CC BY 4.0).
