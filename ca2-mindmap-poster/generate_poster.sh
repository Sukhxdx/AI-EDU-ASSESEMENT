#!/usr/bin/env bash
# Render the CA2 mind-map poster to A2 landscape PDF and PNG.
set -euo pipefail
DIR="$(cd "$(dirname "$0")" && pwd)"
if [[ ! -d /tmp/node_modules/puppeteer-core ]]; then
  echo "Installing puppeteer-core in /tmp ..."
  (cd /tmp && npm install --no-save puppeteer-core@23)
fi
node "${DIR}/render.cjs"
