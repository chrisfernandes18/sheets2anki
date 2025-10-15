sources = __init__.py remote_decks/*.py

.PHONY: .pipenv ## Check that pipenv is installed
.pipenv:
	@pipenv --version || echo 'Please install pipenv: https://pipenv.pypa.io/en/latest/'

.PHONY: install ## Install the package, dependencies, and pre-commit for local development
install:
	pipenv install --dev
	pipenv run pre-commit install -t pre-push -t pre-commit

.PHONY: format
format: .pipenv ## Auto-format python source files
	pipenv run ruff check --fix $(sources)
	pipenv run ruff format $(sources)

.PHONY: lint ## Lint python source files
lint: .pipenv
	pipenv run ruff check $(sources)
	pipenv run ruff format --check $(sources)

.PHONY: quality ## Run all quality checks
quality: .pipenv format lint
	make format
	make lint

.PHONY: install-addon ## Install the addon to Anki for local development
install-addon:
	rm -rf /Users/$(USER)/Library/Application\ Support/Anki2/addons21/$(ID)/ && \
    mkdir -p /Users/$(USER)/Library/Application\ Support/Anki2/addons21/$(ID)/ && \
	cp -af __init__.py config.json meta.json remote_decks /Users/$(USER)/Library/Application\ Support/Anki2/addons21/$(ID)/
