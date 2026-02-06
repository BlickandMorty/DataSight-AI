# make install = create venv + install deps
# make run = run main.py
# make test = run tests
# make setup-env = create .env
#
# override PYTHON_PATH if python3.12 is somewhere else on your system:
#   make install PYTHON_PATH=/usr/bin/python3.12

PYTHON_PATH ?= $(shell command -v python3.12 2>/dev/null || command -v python3 2>/dev/null || echo python3)
VENV_PATH := .venv

install:
	@$(PYTHON_PATH) -c "import sys; v=sys.version_info; exit(0 if v.major==3 and v.minor==12 else 1)" 2>/dev/null || \
		{ echo "Python 3.12 not found. install it or set PYTHON_PATH:"; \
		  echo "  macOS:   brew install python@3.12"; \
		  echo "  linux:   sudo apt install python3.12  (or your distro's package)"; \
		  echo "  windows: download from python.org"; \
		  echo "  then: make install PYTHON_PATH=/path/to/python3.12"; \
		  exit 1; }
	rm -rf $(VENV_PATH)
	$(PYTHON_PATH) -m venv $(VENV_PATH)
	. $(VENV_PATH)/bin/activate && pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

run:
	. $(VENV_PATH)/bin/activate && python main.py

test:
	. $(VENV_PATH)/bin/activate && python tests.py

setup-env:
	bash install.sh
