# Sheets2Anki Add-on

#import sys os
import sys
import os

# Obtain the absolute path of the current directory (where __init__.py is located)
addon_path = os.path.dirname(__file__)

# Add the 'libs' folder to sys.path
libs_path = os.path.join(addon_path, 'remote_decks', 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)
    
# Anki integration class

from aqt import mw
from aqt.utils import showInfo, qconnect
from aqt.qt import QAction, QMenu, QKeySequence

try:
    from .remote_decks.main import add_new_deck
    from .remote_decks.main import sync_decks as sDecks
    from .remote_decks.main import remove_remote_deck as rDecks
    from .remote_decks.libs.org_to_anki.utils import getAnkiPluginConnector as getConnector
except Exception as e:
    showInfo(f"Error importing modules from the sheets2anki plugin:\n{e}")
    raise

errorTemplate = """
Hello! It seems an error occurred during execution.

The error was: {}.

If you want me to fix it, please report it here: https://github.com/sebastianpaez/sheets2anki

Make sure to provide as much information as possible, especially the file that caused the error.
"""

def add_deck():
    """Function to add a new remote deck."""
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        add_new_deck()
    except Exception as e:
        print(f"Error in add_deck: {e.with_traceback()}")  # Debug message
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        ankiBridge.stopEditing()

def sync_decks():
    """Function to sync remote decks."""
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        sDecks()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        showInfo("Synchronization complete")
        ankiBridge.stopEditing()

def remove_remote():
    """Function to remove a remote deck."""
    try:
        ankiBridge = getConnector()
        ankiBridge.startEditing()
        rDecks()
    except Exception as e:
        errorMessage = str(e)
        showInfo(errorTemplate.format(errorMessage))
        if ankiBridge.getConfig().get("debug", False):
            import traceback
            trace = traceback.format_exc()
            showInfo(str(trace))
    finally:
        ankiBridge.stopEditing()

# Confirm that mw is not None before adding new action to the menu
if mw is not None:
    remoteDecksSubMenu = QMenu("Manage sheets2anki Decks", mw)
    mw.form.menuTools.addMenu(remoteDecksSubMenu)

    # Add action to "Add New Remote Deck"
    remoteDeckAction = QAction("Add New sheets2anki Remote Deck", mw)
    remoteDeckAction.setShortcut(QKeySequence("Ctrl+Shift+A"))
    qconnect(remoteDeckAction.triggered, add_deck)
    remoteDecksSubMenu.addAction(remoteDeckAction)

    # Action to "Sync remote Decks"
    syncDecksAction = QAction("Sync Decks", mw)
    syncDecksAction.setShortcut(QKeySequence("Ctrl+Shift+S"))
    qconnect(syncDecksAction.triggered, sync_decks)
    remoteDecksSubMenu.addAction(syncDecksAction)

    # Action to "Disconnect a remote Deck"
    remove_remote_deck = QAction("Disconnect a remote Deck", mw)
    remove_remote_deck.setShortcut(QKeySequence("Ctrl+Shift+D"))
    qconnect(remove_remote_deck.triggered, remove_remote)
    remoteDecksSubMenu.addAction(remove_remote_deck)
