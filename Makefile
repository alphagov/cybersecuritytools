# Run `make` for a single test run
# or `make watch` for a continuous pipeline that reruns on changes.
#
# Comments to cyber.security@digital.cabinet-office.gov.uk
# This is free and unencumbered software released into the public domain.

.SILENT: test watch checks poetry.lock

test: formatting
	poetry run pytest
	echo "✔️ Tests passed!"

formatting: poetry.lock cybersecuritytools
	poetry run isort --profile=black cybersecuritytools
	poetry run black cybersecuritytools

poetry.lock: pyproject.toml
	set -e
	echo "⏳ installing..."
	poetry update
	echo "✔️ Poetry dependencies installed!"

watch:
	echo "✔️ Watch setup, save a python file to trigger test pipeline"
	pipenv run watchmedo shell-command --drop --ignore-directories --patterns="*.py" --ignore-patterns="*#*" --recursive --command='clear && make --no-print-directory test' .
