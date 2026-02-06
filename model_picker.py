#!/usr/bin/env python3
"""
list available gemini models for this key and suggest a default.
optionally writes GEMINI_MODEL to .env.
"""

import os
import re
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("no GEMINI_API_KEY found. add it to .env first.")
    raise SystemExit(1)

client = genai.Client(api_key=api_key)

models = []
for m in client.models.list():
    if "generateContent" in m.supported_actions:
        models.append(m.name)

if not models:
    print("no models returned for this key.")
    raise SystemExit(1)

print("models that support generateContent:")
for name in models:
    print(f"- {name}")

# pick a best model by simple heuristic
# prefer latest flash (2.5 > 2.0 > 1.5) then any gemini flash

def score(name: str) -> tuple:
    # parse like 'models/gemini-2.5-flash'
    m = re.search(r"gemini-(\d+)\.(\d+)-flash", name)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2))
        return (3, major, minor)  # highest priority
    m = re.search(r"gemini-(\d+)-(\d+)-flash", name)
    if m:
        major = int(m.group(1))
        minor = int(m.group(2))
        return (3, major, minor)
    if "gemini" in name and "flash" in name:
        return (2, 0, 0)
    if "gemini" in name:
        return (1, 0, 0)
    return (0, 0, 0)

recommended = sorted(models, key=score, reverse=True)[0]
print(f"\nrecommended: {recommended}")

# map models/<name> to plain name
plain = recommended.replace("models/", "")

resp = input("write this to .env as GEMINI_MODEL? (y/n): ").strip().lower()
if resp == "y":
    # append or update .env
    lines = []
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            lines = f.read().splitlines()
    new_lines = []
    found = False
    for line in lines:
        if line.startswith("GEMINI_MODEL="):
            new_lines.append(f"GEMINI_MODEL={plain}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"GEMINI_MODEL={plain}")
    with open(".env", "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines) + "\n")
    print("saved GEMINI_MODEL to .env")
else:
    print("ok, not writing .env")
