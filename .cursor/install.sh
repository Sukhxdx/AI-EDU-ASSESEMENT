#!/usr/bin/env bash
# Idempotent dependency setup for the AI Edu Assessment project.
# Prepares the FastAPI backend (Python venv) and the Expo mobile app (npm).
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> Ensuring python venv support is present"
if ! dpkg -s python3.12-venv >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3.12-venv
fi

echo "==> Backend: creating/refreshing virtualenv"
cd "$REPO_ROOT/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv
fi
# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install --upgrade pip

# No GPU in the Cloud Agent VM: install the CPU build of the pinned torch
# version first so pip does not pull the multi-GB CUDA wheel. The subsequent
# requirements install then sees torch as already satisfied.
pip install torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt

# NLTK tokenizer data used for text processing.
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('punkt_tab', quiet=True)"
deactivate

echo "==> Mobile: installing npm dependencies"
cd "$REPO_ROOT/mobile"
npm install

echo "==> Install complete"
