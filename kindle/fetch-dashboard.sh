#!/usr/bin/env sh
# Replaces kindle-dash's local/fetch-dashboard.sh.
"$(dirname "$0")/../xh" -d -q -o "$1" get https://raw.githubusercontent.com/LShen67/kindle-dashboard/main/dashboard.png
