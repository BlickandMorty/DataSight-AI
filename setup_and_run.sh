#!/bin/bash
# one-command setup + run
# runs venv setup, installs deps, prompts for key/model if needed, then runs the audit

set -e

# go to this script's folder
cd "$(dirname "$0")"

say() { printf "• %s\n" "$1"; }

echo "datasight setup"

# pick a python (3.12 only for now)
PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if command -v python3.12 >/dev/null 2>&1; then
    PYTHON_BIN="python3.12"
  elif command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  else
    echo "python3 not found. install python 3.12."
    exit 1
  fi
fi

py_ver=$($PYTHON_BIN - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)

case "$py_ver" in
  3.12) ;;
  *)
    echo "python $py_ver detected. please use python 3.12."
    echo "tip: brew install python@3.12"
    exit 1
    ;;
esac

if [ -d ".venv" ] && [ -x ".venv/bin/python" ]; then
  venv_ver=$(.venv/bin/python - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
  )
  case "$venv_ver" in
    3.12) ;;
    *)
      say "existing .venv is python $venv_ver, rebuilding with $PYTHON_BIN"
      rm -rf .venv
      ;;
  esac
fi

if [ ! -d ".venv" ]; then
  say "creating .venv with $PYTHON_BIN"
  $PYTHON_BIN -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

say "installing dependencies"
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt

if [ ! -f .env ]; then
  say "creating .env"
  bash install.sh
fi

# if no model is set, try the model picker once (interactive)
if [ -z "${GEMINI_MODEL:-}" ] && [ -f "model_picker.py" ]; then
  say "no GEMINI_MODEL set, trying model picker"
  python model_picker.py || echo "model picker could not find models for this key. continuing."
fi

# allow non-interactive usage:
# CSV_FILE=your.csv ./setup_and_run.sh
# or: ./setup_and_run.sh --file your.csv
csv_input=""
while [ $# -gt 0 ]; do
  case "$1" in
    --file|-f)
      csv_input="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "$csv_input" ] && [ -n "$CSV_FILE" ]; then
  csv_input="$CSV_FILE"
fi

# pick a csv (default = messy_sample.csv if it exists)
default_csv="messy_sample.csv"
if [ ! -f "$default_csv" ]; then
  # fall back to the first csv in the folder
  for f in *.csv; do
    if [ -f "$f" ]; then
      default_csv="$f"
      break
    fi
  done
fi

# gui file picker only (no prompt). if none available, exit with instructions.
if [ -z "$csv_input" ]; then
  if command -v osascript >/dev/null 2>&1; then
    csv_input=$(osascript -e 'POSIX path of (choose file with prompt "pick a csv file" of type {"public.comma-separated-values-text","public.text"})' 2>/dev/null | tr -d '\r')
  elif command -v zenity >/dev/null 2>&1; then
    csv_input=$(zenity --file-selection --file-filter="CSV files (csv) | *.csv" --title="pick a csv file" 2>/dev/null)
  elif command -v kdialog >/dev/null 2>&1; then
    csv_input=$(kdialog --getopenfilename . "*.csv" --title "pick a csv file" 2>/dev/null)
  elif command -v yad >/dev/null 2>&1; then
    csv_input=$(yad --file --file-filter="CSV files | *.csv" --title="pick a csv file" 2>/dev/null)
  fi
fi

if [ -z "$csv_input" ]; then
  echo "no file picker found or you cancelled."
  echo "run with: CSV_FILE=path/to/file.csv ./setup_and_run.sh"
  echo "or: ./setup_and_run.sh --file path/to/file.csv"
  exit 1
fi

if [ ! -f "$csv_input" ]; then
  echo "file not found: $csv_input"
  echo "put the csv in this folder or pass a full path."
  exit 1
fi

say "running audit"
python main.py --file "$csv_input"
