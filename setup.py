#!/usr/bin/env python3
"""
cross-platform setup + run script for datasight.
works on macos, linux, and windows.

usage:
    python setup.py
    python setup.py --file your.csv
    python setup.py --skip-setup --file your.csv
"""

import os
import sys
import subprocess
import platform
import argparse
import shutil

def say(msg):
    print(f"  {msg}")

def get_os():
    s = platform.system().lower()
    if s == "darwin":
        return "macos"
    elif s == "windows":
        return "windows"
    else:
        return "linux"

def find_python():
    """find a python 3.12 binary on this system."""
    # check if we're already running 3.12
    if sys.version_info[:2] == (3, 12):
        return sys.executable
    # try common names
    for name in ["python3.12", "python3", "python"]:
        path = shutil.which(name)
        if path:
            try:
                out = subprocess.check_output([path, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"], text=True).strip()
                if out == "3.12":
                    return path
            except Exception:
                continue
    return None

def venv_python():
    """return the path to the venv python binary."""
    current_os = get_os()
    if current_os == "windows":
        return os.path.join(".venv", "Scripts", "python.exe")
    return os.path.join(".venv", "bin", "python")

def venv_exists():
    return os.path.isfile(venv_python())

def create_venv(py_bin):
    say(f"creating .venv with {py_bin}")
    subprocess.check_call([py_bin, "-m", "venv", ".venv"])

def install_deps():
    vpy = venv_python()
    say("installing dependencies")
    subprocess.check_call([vpy, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], stdout=subprocess.DEVNULL)
    subprocess.check_call([vpy, "-m", "pip", "install", "-r", "requirements.txt"])

def setup_env():
    """create .env if it doesn't exist."""
    if os.path.exists(".env"):
        return
    say("no .env found. lets create one.")
    if not sys.stdin.isatty():
        say("not interactive. copy .env.example to .env and add your key.")
        return
    key = input("  paste your gemini api key (leave blank to skip): ").strip()
    if not key:
        say("no key entered. you can add it later to .env.")
        return
    with open(".env", "w", encoding="utf-8") as f:
        f.write(f'GEMINI_API_KEY="{key}"\n')
    say(".env created.")

def pick_csv_gui():
    """try to open a native file picker. returns path or None."""
    current_os = get_os()
    try:
        if current_os == "macos":
            result = subprocess.check_output(
                ["osascript", "-e", 'POSIX path of (choose file with prompt "pick a csv file" of type {"public.comma-separated-values-text","public.text"})'],
                text=True
            ).strip()
            return result
        elif current_os == "linux":
            for cmd in ["zenity", "kdialog", "yad"]:
                if shutil.which(cmd):
                    if cmd == "zenity":
                        result = subprocess.check_output(
                            ["zenity", "--file-selection", "--file-filter=CSV files (csv) | *.csv", "--title=pick a csv file"],
                            text=True
                        ).strip()
                    elif cmd == "kdialog":
                        result = subprocess.check_output(
                            ["kdialog", "--getopenfilename", ".", "*.csv", "--title", "pick a csv file"],
                            text=True
                        ).strip()
                    elif cmd == "yad":
                        result = subprocess.check_output(
                            ["yad", "--file", "--file-filter=CSV files | *.csv", "--title=pick a csv file"],
                            text=True
                        ).strip()
                    return result
        elif current_os == "windows":
            # use tkinter file dialog (comes with python on windows)
            script = (
                'import tkinter as tk; from tkinter import filedialog; '
                'root = tk.Tk(); root.withdraw(); '
                'f = filedialog.askopenfilename(title="pick a csv file", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]); '
                'print(f)'
            )
            result = subprocess.check_output([sys.executable, "-c", script], text=True).strip()
            if result:
                return result
    except Exception:
        pass
    return None

def main():
    parser = argparse.ArgumentParser(description="datasight setup + run")
    parser.add_argument("--file", "-f", default=None, help="csv file to audit")
    parser.add_argument("--skip-setup", action="store_true", help="skip venv/deps setup (just run)")
    parser.add_argument("--auto-fix", action="store_true", help="apply fixes and save fixed csv")
    args = parser.parse_args()

    current_os = get_os()
    print(f"datasight setup ({current_os})")

    # go to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    if not args.skip_setup:
        # find or verify python 3.12
        py_bin = find_python()
        if not py_bin:
            print("python 3.12 not found. install it first:")
            if current_os == "macos":
                print("  brew install python@3.12")
            elif current_os == "linux":
                print("  sudo apt install python3.12  (or your distro's package)")
            elif current_os == "windows":
                print("  download from https://www.python.org/downloads/")
            sys.exit(1)

        say(f"found python 3.12 at {py_bin}")

        # check existing venv version
        if venv_exists():
            try:
                out = subprocess.check_output([venv_python(), "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"], text=True).strip()
                if out != "3.12":
                    say(f"existing .venv is python {out}, rebuilding")
                    shutil.rmtree(".venv")
            except Exception:
                shutil.rmtree(".venv")

        if not venv_exists():
            create_venv(py_bin)

        install_deps()
        setup_env()

    # figure out which csv to audit
    csv_file = args.file or os.environ.get("CSV_FILE", "")

    if not csv_file:
        csv_file = pick_csv_gui()

    if not csv_file:
        print("no file selected.")
        print(f"  python setup.py --file path/to/file.csv")
        print(f"  or set CSV_FILE=path/to/file.csv")
        sys.exit(1)

    if not os.path.isfile(csv_file):
        print(f"file not found: {csv_file}")
        sys.exit(1)

    # run the audit
    say("running audit")
    cmd = [venv_python(), "main.py", "--file", csv_file]
    if args.auto_fix:
        cmd.append("--auto-fix")
    subprocess.check_call(cmd)

if __name__ == "__main__":
    main()
