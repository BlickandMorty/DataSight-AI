# DataSight

audits a csv for missing values, outliers, and likely data issues using rules + gemini.

requirements: python 3.12, internet access, and a gemini api key.

works on macos, linux, and windows.

## quickstart (any os)

the easiest way on any platform. this handles venv, deps, key prompt, and csv picker:

```sh
python3 setup.py
```

or with a specific file:

```sh
python3 setup.py --file your.csv
```

on windows just use `python` instead of `python3`. it auto-detects your os and opens the right file picker (Finder on macos, zenity/kdialog on linux, tkinter dialog on windows).

## run it (macos/linux shell script)

```sh
./setup_and_run.sh
```

this does everything: venv, deps, key prompt, model check, csv picker.

non-interactive option:

```sh
CSV_FILE=your.csv ./setup_and_run.sh
# or
./setup_and_run.sh --file your.csv
```

on macos it opens a file picker. on linux it tries zenity/kdialog/yad if installed.
if no picker is available, use CSV_FILE or --file.

## manual setup (any os)

```sh
python3.12 -m venv .venv

# macos/linux:
source .venv/bin/activate

# windows (powershell):
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
bash install.sh  # creates .env and lets you paste your key

# or do it manually:
# cp .env.example .env
# add GEMINI_API_KEY to .env

python main.py
```

## makefile shortcuts (optional)

```sh
make install
make setup-env
make run
make test
```

the makefile auto-detects your python3.12 location. if it can't find it, override it:

```sh
make install PYTHON_PATH=/usr/bin/python3.12
```

## how it works (plain english)

so there are three main parts.

the `main.py` which is the control room file or the landing page of the project that facilitates outputting and displaying overall results, it facilitates file upload, etc.

then we have the `core/data_processor.py`: this is the engine that looks at the csv. Essentially, the dirty or otherwise messy data that must be analyzed and corrected or simply analyzed. What it does is it uses Pandas, which is a python library. it is a library of tools, functions, and classes for data manipulation and analysis. This thing works with tabular data like csv spreadsheets and such. its like excel, SQL and python in one tool basically.

In Pandas the main object is a DataFrame, so like 2d tables, columns, rows, nulls, like a spreadsheet, categorically.

```
df = a table
df.columns = column names
df["age"] = one column
df.head() = first few rows
```

then we have `core/interpreter.py`: this is the brain. the detective. it receives the metadata dictionary (that summary sheet from data_processor) and its job is to find whats wrong with the data and suggest fixes. it does this two ways: rule-based checks (the manual detective work) and AI-based checks (the smart detective via gemini).

---

### how its being used in my code

so first i import pandas as pd, which basically means to just import pandas and give it the nickname pd.

```python
import pandas as pd
def get_metadata(df):
    return {
        "columns": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "head": df.head(3).to_dict()
    }
```

both main.py and data_processor.py files are using `import pandas as pd`. so they are both using pandas for something... lets keep that in mind.

### In main.py...

```python
df = pd.read_csv(csv_file)
```

this means: "load this .csv file and turn it into a DataFrame table." so now `df` is my dataset.

so `df` is just 'dataframe'. it is a standard table like 2d structure. and in this syntax sentence `df = pd.read_csv(csv_file)` here is what the computer is saying: "ill make this a dataframe. Next, ill have pandas (pd) use its cool function that reads csv files, to read and convert this csv file into a dataframe or table structure of this data."

### In data_processor.py...

```python
def get_metadata(df):
    return {
        "columns": list(df.columns),
        "null_counts": df.isnull().sum().to_dict(),
        "head": df.head(3).to_dict()
    }
```

`def` means to 'define' (keyword that 'declares' im creating a reusable function). So basically im just letting the world know that "hey...i am creating a function that will be reused during this process."

`def get_metadata(df):` creates a function named `get_metadata`. it takes one parameter `df`, which is the dataframe we had created from the csv file. the `:` signals that whats next is the function body. so the guts of this thing.

`return {...}` sends back a **dictionary** (Python's key-value data structure). the curly braces `{}` denote a dict with 3 key-value pairs.

---

### ...so what IS a dictionary actually

a dictionary is literally just **labeled storage**. thats it. think of it like a form you fill out. each field has a label and a value next to it.

```python
person = {
    "name": "Alice",      # label: value
    "age": 30,            # label: value
    "city": "New York"    # label: value
}
```

the label is called the **key**. the value is called the **value**. together they are a **key-value pair**. so when someone says "3 key-value pairs" they just mean there are 3 labeled slots filled in. like a form with 3 fields completed.

so in my code when it says:

```python
return {
    "columns": list(df.columns),        # key-value pair 1
    "null_counts": df.isnull().sum().to_dict(),  # key-value pair 2
    "head": df.head(3).to_dict()        # key-value pair 3
}
```

its literally just saying "here is a form with 3 filled out fields. the first field is labeled 'columns' and its value is the column names. the second field is labeled 'null_counts' and its value is how many nulls are in each column. the third field is labeled 'head' and its value is the first 3 rows as a preview."

and to access something in a dictionary you just use the label:

```python
metadata["columns"]     # grabs the column names
metadata["null_counts"] # grabs the null counts
```

its like saying "give me what's in the 'columns' field."

---

### ...so how is dictionary different from dataframe

both are data structures but they do different things.

- **DataFrame** = a full spreadsheet. rows, columns, the whole table. this is where the actual CSV data lives.
- **Dictionary** = a labeled form. its lighter. its used to **package and transport** specific info.

so in my project what happens is... the CSV becomes a DataFrame (the full spreadsheet). then `get_metadata()` pulls specific info OUT of that spreadsheet and puts it into a dictionary (a form). the dictionary is easier to pass around and send to the AI than the whole massive spreadsheet.

think of it like... the DataFrame is the whole filing cabinet. the dictionary is just the summary sheet you pull out of it.

---

### Now the interpreter.py...

this is the brain. the detective. it receives the metadata dictionary (that summary sheet from data_processor) and its job is to find whats wrong with the data and suggest fixes. it does this two ways...

#### Rule-based checks (the manual detective work)

it looks at the null counts from the metadata and loops through each column. if a column has missing values it creates a problem report for it.

```python
nulls = metadata.get('null_counts', {})
```

this line is saying "grab the null_counts from the metadata dictionary. if it doesnt exist for some reason, just give me an empty dictionary so nothing breaks."

then it loops:

```python
for col, count in nulls.items():
    if count > 0:
        audit_trail.append({...})
```

so `nulls` is a dictionary like `{"Name": 0, "Age": 5, "Salary": 2}`. `.items()` gives us each label-value pair one at a time. `col` is the label (column name) and `count` is the value (how many nulls). the `for` loop goes through each one. and `if count > 0` means "only care about columns that actually have missing values." if there are missing values it appends (adds to the bottom of the list) a problem report dictionary.

so after the loop `audit_trail` is a list of all the problems found. like a list of sticky notes each describing one issue.

#### AI-based checks (the smart detective)

after the rule-based stuff it sends the metadata to Google's Gemini AI. why? because the rules can only catch what we programmed them to catch. the AI can spot patterns and issues we didnt think of.

```python
response = client.models.generate_content(model=model_name, contents=config.AUDIT_PROMPT.format(metadata=metadata))
summary = response.text
```

this sends the metadata to Gemini with a prompt (instructions) and gets back a natural language summary of what it found.

#### Why the preview (head 3 rows) matters

the AI doesnt have access to our CSV file. it can only see what we send it. if we only sent column names and null counts it would be blind to what the actual data looks like. the 3 row preview gives it eyes. it can see if values are weird like `"N/A"` strings instead of actual empty values. 3 rows is enough to see the pattern. sending all 10,000 rows would be slow and expensive (AI APIs charge per amount of text sent).

#### What it returns

it returns two things back to main.py:

```python
return audit_trail, summary
```

- `audit_trail` = the list of problem reports (from the rule-based checks)
- `summary` = the AI's natural language analysis

---

### Back in main.py... displaying everything

main.py gets both of those things back and displays them. the audit trail gets printed as a numbered list. each item shows the problem and a suggested fix. if `auto_fix` is turned on (True) it actually runs the fix functions and saves a new cleaned CSV file.

`auto_fix` is like a toggle switch. by default its off (False) so it just shows you the problems. if you turn it on (True) it actually fixes them. this is smart because sometimes you want to **see** the problems first before blindly fixing them. you wouldnt want a machine changing your data without you reviewing it first.

---

### The overall flow one more time

```
1. main.py loads the CSV into a DataFrame (the spreadsheet)
2. main.py sends the DataFrame to data_processor.py
3. data_processor pulls out key info and packages it into a dictionary (the summary sheet)
4. main.py sends that dictionary to interpreter.py
5. interpreter runs rule-based checks (finds nulls) and AI checks (finds deeper issues)
6. interpreter sends back the problems and AI summary
7. main.py displays everything to the user
8. optionally fixes the data if auto_fix is on
```

main.py is the boss that coordinates. data_processor is the scanner. interpreter is the brain. but nothing actually "lives" in the other files. main.py is borrowing their logic. the data stays in main.py the whole time. the other files just process it and send results back. like calling a function on a calculator. you give it numbers it gives you an answer. youre still holding the calculator.

## use your own data

- replace `dirty_data.csv` in `main.py`, or
- run from python:

```sh
python -c "from main import run_audit; run_audit('your_file.csv')"
```

## configuration

- `.env` must include `GEMINI_API_KEY`.
- edit `config.py` to change the prompt.

if the key is missing, `main.py` will prompt you once and write `.env` for you.
if you get a model 404, set `GEMINI_MODEL` in `.env`.

## model picker (optional)

this lists the models your key can use and suggests a default.

```sh
python model_picker.py
```

## docker

```sh
docker build -t datasight .
docker run --env-file .env datasight
```

the dockerfile uses a pinned image digest for reproducible builds.

## tests

```sh
python tests.py
```

ai tests are skipped by default. run them with:

```sh
RUN_AI_TESTS=1 python tests.py
```

## try a messy file

```sh
python -c "from main import run_audit; run_audit('messy_sample.csv')"
```

if something crashes, the full error gets written to `datasight_error.log`.

## auto-fix (optional)

```sh
python main.py --file messy_sample.csv --auto-fix
```

## project layout

- `main.py`: entry point
- `core/`: processing + model call
- `config.py`: prompt text
- `dirty_data.csv`: example data
- `messy_sample.csv`: messier example data

## contributing

see `CONTRIBUTING.md`.

## license

see `LICENSE`.
