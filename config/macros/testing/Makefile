venv:
	python3 -m venv .venv

install: venv
	. .venv/bin/activate && pip install -r requirements.txt

sample:
	. .venv/bin/activate && python render_gcode.py

test:
	. .venv/bin/activate && python -m pytest tests/ -v
