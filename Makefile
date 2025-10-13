install:
	pipenv install

# Local development command
update-addon:
	rm -rf /Users/$(USER)/Library/Application\ Support/Anki2/addons21/$(ID)/ && \
    mkdir -p /Users/$(USER)/Library/Application\ Support/Anki2/addons21/$(ID)/ && \
	cp -af __init__.py config.json meta.json remote_decks /Users/$(USER)/Library/Application\ Support/Anki2/addons21/$(ID)/
