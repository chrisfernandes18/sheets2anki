# Local Development

## Pre-requirements

1. `python` installed.

2. `pipenv` installed.

## Setup

### Install Dependencies

```sh
make install
```

Should install all the necessary libraries.

### Running code locally

1. Locate where your Anki add-ons are installed. On macOS this would be at the path `/Users/$($USER)/Library/Application\ Support/Anki2/addons21/`. This is where you can run the following command to copy the files right now into an addon of a given ID.

    ```sh
    make update-addon USER=test ID=12345678910
    ```

2. When debugging I use two methods. Either using the function `showInfo` to open up a pop-up window or [following these instructions](https://addon-docs.ankiweb.net/console-output.html) I run in a terminal, which will open up Anki, but also print out stdout messages from within the code.

    ```sh
    /Applications/Anki.app/Contents/MacOS/launcher
    ```

3. Other methods, are using the `if __name__ == "__main__"` within files and run the file name to be able to test helper functions.
