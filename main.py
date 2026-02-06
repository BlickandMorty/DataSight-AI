import pandas as pd
import os
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv
from core.interpreter import get_ai_audit
from core.data_processor import get_metadata

def log_error(e):
    # write a simple error report so debugging is easy later
    try:
        with open("datasight_error.log", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().isoformat()}] {type(e).__name__}: {e}\n")
            f.write(traceback.format_exc())
            f.write("\n")
        print("   i saved the full error to datasight_error.log")
    except Exception:
        pass

def ensure_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key
    if not sys.stdin.isatty():
        print("❌ Error: GEMINI_API_KEY not found and no interactive prompt available")
        return None
    print("🔑 no GEMINI_API_KEY found. i can create .env now.")
    key = input("paste your gemini api key (leave blank to cancel): ").strip()
    if not key:
        print("❌ no key entered. stopping.")
        return None
    try:
        write_env_value("GEMINI_API_KEY", key)
        load_dotenv(override=True)
        print("✅ .env saved.")
        return os.getenv("GEMINI_API_KEY")
    except Exception as e:
        print(f"❌ could not write .env: {e}")
        return None

def write_env_value(key, value):
    # update .env without wiping other settings
    lines = []
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    new_lines = []
    found = False
    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f'{key}="{value}"')
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f'{key}="{value}"')
    with open(".env", "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")

# load .env so GEMINI_API_KEY is available
load_dotenv()

def run_audit(csv_file="dirty_data.csv", auto_fix=False):
    """
    run a datasight audit on a csv.
    csv_file: path to the csv (default: dirty_data.csv)
    auto_fix: if true, apply suggested fixes and save fixed_<file>.csv
    """
    try:
        api_key = ensure_api_key()
        if not api_key:
            print("📝 you can also create it manually:")
            print("   cp .env.example .env")
            print("   # then edit .env and add your actual api key")
            return
        if not os.path.exists(csv_file):
            print(f"❌ Error: File '{csv_file}' not found")
            print(f"   Make sure the file is in the same folder as main.py")
            return
        df = pd.read_csv(csv_file)
        if df.empty:
            print(f"❌ Error: The file '{csv_file}' is empty (no data rows)")
            return
        metadata = get_metadata(df)
        print("datasight audit")
        print(f"file: {csv_file}")
        print(f"size: {len(df)} rows × {len(df.columns)} columns")
        # ask gemini for a summary + trail
        audit_trail, summary = get_ai_audit(metadata, api_key, return_trail=True)
        print("\nfindings")
        if audit_trail:
            for idx, item in enumerate(audit_trail, 1):
                print(f"- {idx}. {item['description']}")
                if 'suggested_fix' in item:
                    print(f"  fix: {item['suggested_fix']}")
        else:
            print("- no rule-based issues found")
        # if auto_fix is on, apply any fix functions
        if auto_fix:
            for item in audit_trail:
                if 'fix_function' in item and callable(item['fix_function']):
                    df = item['fix_function'](df)
            print(f"\nauto-fix: saved fixed_{csv_file}")
            df.to_csv("fixed_" + csv_file, index=False)
        print("\nsummary")
        print(summary)
        # npc-style hints
        lower_summary = summary.lower()
        if "quota exhausted" in lower_summary or "resource_exhausted" in lower_summary:
            print("\nwhat next (npc)")
            print("hey, traveler. your ai quota is empty right now.")
            print("come back after it resets, or enable billing.")
            print("you can still use rule checks even without ai.")
        elif "model not available" in lower_summary or "not available" in lower_summary:
            print("\nwhat next (npc)")
            print("that model door is locked for your key.")
            print("run model_picker.py and set GEMINI_MODEL in .env.")
            print("then try again.")
        else:
            print("\nwhat next (npc)")
            print("looks like the path is clear.")
            print("try a different csv or turn on --auto-fix.")
    except pd.errors.ParserError:
        print(f"❌ Error: Could not read '{csv_file}'")
        print("   Make sure it's a valid CSV file")
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        print("   See README.md for help")
        log_error(e)

if __name__ == "__main__":
    # run: python main.py --file your_file.csv --auto-fix
    import argparse
    parser = argparse.ArgumentParser(description="run a datasight audit")
    parser.add_argument("--file", default="dirty_data.csv", help="csv file to audit")
    parser.add_argument("--auto-fix", action="store_true", help="apply fix functions and save fixed_<file>.csv")
    args = parser.parse_args()
    run_audit(args.file, auto_fix=args.auto_fix)
