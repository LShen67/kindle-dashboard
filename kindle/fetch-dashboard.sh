#!/usr/bin/env sh
# Replaces kindle-dash's local/fetch-dashboard.sh.
# Change YOUR-GITHUB-NAME and REPO-NAME to your GitHub repository.
"$(dirname "$0")/../xh" -d -q -o "$1" get https://raw.githubusercontent.com/YOUR-GITHUB-NAME/REPO-NAME/main/dashboard.png
