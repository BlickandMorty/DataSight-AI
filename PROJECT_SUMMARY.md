# datasight project notes

this is the single doc that explains the whole project in plain english.

i am keeping this in the same tone as my notes so i can read it later and immediately know what is going on.

---

## what this project is doing

i take a csv, turn it into a pandas dataframe (a table), pull out a summary, then ask gemini to audit the summary. i also do a basic rule pass so i can catch missing values even without the model.

the output is:
- a list of issues (audit trail)
- a natural language summary from gemini
- optional auto-fixes that write a new csv

---

## the 3 main parts (mental model)

- `main.py` = control room. it loads the csv, calls the helpers, and prints the results.
- `core/data_processor.py` = scanner. it looks at the csv and pulls out a small summary.
- `core/interpreter.py` = brain. it runs simple rules, then asks gemini for a deeper read.

so main.py is the coordinator, the other files are helpers. the data itself stays in main.py the whole time.

---

## the data flow (step by step)

1. main.py reads the csv into a pandas dataframe
2. main.py calls `get_metadata(df)` from data_processor
3. data_processor returns a small dictionary summary
4. main.py sends that summary to interpreter
5. interpreter does:
   - rule pass (missing values)
   - gemini pass (pattern/logic issues)
6. interpreter returns (audit_trail, summary)
7. main.py prints results and optionally writes fixed_<file>.csv

---

## why i use a dictionary here

a dataframe is the full spreadsheet. big and heavy.
a dictionary is a labeled form. light and cheap to pass around.

example dictionary:

```python
metadata = {
    "columns": ["name", "age"],
    "null_counts": {"name": 0, "age": 2},
    "head": {"name": {0: "alice"}, "age": {0: 30}}
}
```

so the model gets a summary sheet instead of the entire filing cabinet.

---

## what each file does (only the important ones)

- `main.py` = entry point. read csv, call helpers, print results, optional auto-fix
- `core/data_processor.py` = builds the metadata dictionary
- `core/interpreter.py` = rule checks + gemini summary
- `config.py` = prompt text sent to gemini
- `requirements.txt` = pinned python dependencies
- `.env.example` = shows what secrets to set
- `install.sh` = creates .env for you (optional helper)
- `Makefile` = shortcut commands (install/run/test/setup-env)
- `setup_and_run.sh` = one script to set up + prompt for csv + run
- `model_picker.py` = lists available models for your key and suggests one
- `tests.py` = small test suite
- `.github/workflows/ci.yml` = github actions test run
- `Dockerfile` = container build option

---

## imports and why they exist

- `pandas` = reads csv and gives us the dataframe tools
- `dotenv` = loads GEMINI_API_KEY from .env
- `os` = read env vars + file checks
- `google.genai` = talk to gemini

---

## how the rules + model work together

- rules are fast and guaranteed: "count missing values per column"
- gemini is for smarter stuff: patterns, logic errors, weird ranges, etc

so if the model fails, i still have rule results.

---

## auto_fix (what it actually means)

- default is off (auto_fix=False)
- if on, it runs any fix functions and saves a new csv
- i keep it off by default because i want to see the issues before edits

---

## how to run

```sh
python main.py
```

or with your own file:

```sh
python main.py --file your_file.csv
```

if you want auto-fix:

```sh
python main.py --file your_file.csv --auto-fix
```

---

## how to test

```sh
python tests.py
```

or:

```sh
make test
```
---

## what is required for github (and do i have it?)

required or basically expected:
- README.md (yes)
- LICENSE (yes)
- .gitignore (yes)
- requirements.txt (yes)
- tests (yes)
- clear entry point (yes)

nice to have:
- CONTRIBUTING.md (yes)
- CI (yes, github actions)
- sample data (yes, dirty_data.csv)
- docker option (yes)
- env template (yes, .env.example)

optional depending on the audience:
- CHANGELOG.md (not needed right now)
- CODE_OF_CONDUCT.md (only needed for bigger communities)
- SECURITY.md (only needed if people report vulns)

so overall the structure is solid. i do not need more docs. i just keep this single summary + the README.

---

## how i should focus future projects

- keep one clear entry point
- keep the core logic in small helper files
- keep config separate
- keep docs to 1 or 2 files max
- have tests + requirements + license + gitignore
- keep sample data if the app needs it

---

## quick note on "does it work"

it works if:
- dependencies install
- GEMINI_API_KEY is set in .env
- the csv is valid

if the key is missing or the csv is broken, main.py prints a clean error and exits.
if it crashes, it writes the full traceback to datasight_error.log.
if the key is missing, main.py will also prompt you once and write .env for you.
