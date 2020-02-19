# In your python env, run `make install` to insall required packages
# and then either `make` for a single test run
# or `make watch` for a continuous pipeline that reruns on changes.
# 
# Comments and/or hate mail to o@tman.me

.SILENT: test install upgrade watch checks

test: checks
	pytest
	echo "✔️ Tests passed!"

checks:
	echo "⏳ running pipeline..."
	set -e
	black -q .
	flake8 --max-line-length=88 .  # in line with black
	mypy --pretty .
	echo "✔️ Checks pipeline passed!"

install:
	set -e
	echo "⏳ installing..."
	pip -q install black flake8 mypy watchdog pyyaml argh pytest
	echo "✔️ Pip dependencies installed!"

upgrade:
	set -e
	wget -q oat.sh/pymakefile -O Makefile
	echo "✔️ Upgraded Makefile!"

watch:
	echo "✔️ Watch setup, save a python file to trigger test pipeline"
	watchmedo shell-command --patterns="*.py" --ignore-patterns="*#*" --recursive --command='clear && make --no-print-directory test' .
