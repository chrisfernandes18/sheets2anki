from aqt import mw
from anki.collection import Collection
from aqt.utils import showInfo
from aqt.qt import QInputDialog, QLineEdit

from .models.remote_deck import RemoteDeck
from .models.remote_deck_config import RemoteDeckConfig

try:
    echo_mode_normal = QLineEdit.EchoMode.Normal
except AttributeError:
    echo_mode_normal = QLineEdit.Normal

from .parse_remote_deck import get_remote_deck

def sync_decks():
    """Function to sync remote decks."""
    col = mw.col
    config = mw.addonManager.getConfig(__name__)
    if not config:
        config = {"remote-decks": {}}

    for deck_key in config["remote-decks"].keys():
        try:
            current_remote_info = config["remote-decks"][deck_key]

            remote_deck_config = RemoteDeckConfig()
            remote_deck_config.url = current_remote_info["url"]
            remote_deck_config.deck_name = current_remote_info["deck_name"]
            remote_deck_config.note_type = current_remote_info["note_type"]
            remote_deck_config.note_type_fields = current_remote_info["note_type_fields"]
            remote_deck_config.notecard_key_field = current_remote_info["notecard_key_field"]

            remote_deck = get_remote_deck(current_remote_info["url"], remote_deck_config.note_type, remote_deck_config.note_type_fields)
            remote_deck.deck_name = remote_deck_config.deck_name
            deck_id = get_or_create_deck(col, remote_deck_config.deck_name)
            create_or_update_notes(col, remote_deck, deck_id, remote_deck_config.note_type, remote_deck_config.notecard_key_field)
        except Exception as e:
            deck_message = f"\nThe following deck failed to sync: {remote_deck_config.deck_name}"
            showInfo(str(e) + deck_message)
            raise

    showInfo("Synchronization complete")

def get_or_create_deck(col: Collection, deck_name: str) -> int:
    """Get or create a deck by name and return its ID.
    Args:
        col (Collection): The Anki collection.
        deck_name (str): The name of the deck.
    Returns:
        int: The ID of the deck.
    """
    deck = col.decks.by_name(deck_name)
    if deck is None:
        deck_id = col.decks.id(deck_name)
    else:
        deck_id = deck["id"]
    return deck_id

def create_or_update_notes(
    col: Collection, 
    remote_deck: RemoteDeck, 
    deck_id: int, 
    note_type_name: str, 
    notecard_key_field: str
) -> None:
    """Create or update notes in the Anki collection based on the remote deck.
    Args:
        col (Collection): The Anki collection.
        remote_deck (RemoteDeck): The remote deck containing notecards.
        deck_id (int): The ID of the deck where notes will be added or updated.
        note_type_name (str): The name of the note type to use.
        notecard_key_field (str): The field used as a unique key for notecards
    """

    # Dictionaries for existing notes
    existing_notes = {}
    existing_note_ids = {}

    notes = col.find_notes(f'deck:"{remote_deck.deck_name}"')

    # Fetch existing notes in the deck
    for nid in notes:
        note = col.get_note(nid)
        key = ''
        
        # Use the specified key field to identify notes
        if notecard_key_field in note:
            key = note[notecard_key_field]
        else:
            continue  # Skip notes without the specified key field
        existing_notes[key] = note
        existing_note_ids[key] = nid

    # Set to keep track of keys from Google Sheets
    gs_keys = set()

    for notecard in remote_deck.notecards:
        card_type = notecard['type']
        fields = notecard['fields']
        tags = notecard.get('tags', [])

        try:
            key = fields[notecard_key_field]
            gs_keys.add(key)

            if key in existing_notes:
                # Update existing note
                note = existing_notes[key]
                for field_name, value in fields.items():
                    note[field_name] = value
                note.tags = tags
                note.flush()
            else:
                # Create new note
                model = col.models.by_name(note_type_name)
                if model is None:
                    showInfo(f"The {note_type_name} model does not exist. Please create a {note_type_name} model in Anki.")
                    continue

                col.models.set_current(model)
                model['did'] = deck_id
                col.models.save(model)

                note = col.new_note(model)
                for field_name, value in fields.items():
                    note[field_name] = value
                note.tags = tags
                col.add_note(note, deck_id)
    
        except Exception as e:
            showInfo(f"Unknown card type '{card_type}' for card '{key}', with error: {e}.\nSkipping.")
            continue    

    # Find notes that are in Anki but not in Google Sheets
    anki_keys = set(existing_notes.keys())
    notes_to_delete = anki_keys - gs_keys

    # Remove the corresponding notes
    if notes_to_delete:
        note_ids_to_delete = [existing_note_ids[key] for key in notes_to_delete]
        col.remove_notes(note_ids_to_delete)

    # Save changes
    col.save()

def add_new_deck() -> None:
    """Function to add a new remote deck."""
    url, ok_pressed = QInputDialog.getText(
        mw, "Add New Remote Deck", "URL of published CSV:", echo_mode_normal, ""
    )
    if not ok_pressed or not url.strip():
        return

    url = url.strip()

    if "output=csv" not in url:
        showInfo("The provided URL does not appear to be a published CSV from Google Sheets.")
        return

    deck_name, ok_pressed = QInputDialog.getText(
        mw, "Deck Name", "Enter the name of the deck:", echo_mode_normal, ""
    )
    if not ok_pressed or not deck_name.strip():
        deck_name = "Deck from CSV"
    names_and_ids = mw.col.models.all_names_and_ids()

    note_type_name_to_id = {item.name: item.id for item in names_and_ids}
    note_type_names = list(note_type_name_to_id.keys())

    note_type_name, ok_pressed = QInputDialog.getItem(
        mw,
        "Select a Note Type to map the deck to",
        "Select a note type:",
        note_type_names,
        0,
        False
    )

    if not ok_pressed or not note_type_name.strip():
        note_type_name = "Basic"
    
    note_type_fields = [field['name'] for field in mw.col.models.get(note_type_name_to_id[note_type_name])['flds']]

    notecard_key_field, ok_pressed = QInputDialog.getItem(
        mw,
        "Select a Notecard Key Field",
        "Select a key field for the notecards:",
        note_type_fields,
        0,
        False
    )

    if not ok_pressed or not notecard_key_field.strip():
        notecard_key_field = note_type_fields[0]

    showInfo(f"Selected note type: {note_type_name} with default key field: {notecard_key_field}")

    config = mw.addonManager.getConfig(__name__)
    if not config:
        config = {"remote-decks": {}}

    if url in config["remote-decks"]:
        showInfo(f"The deck has already been added before: {url}")
        return

    try:
        deck = get_remote_deck(url, note_type_name, note_type_fields)
        deck.deck_name = deck_name
    except Exception as e:
        showInfo(f"Error fetching the remote deck:\n{e}")
        return

    config["remote-decks"][url] = {
        "url": url, 
        "deck_name": deck_name, 
        "note_type": note_type_name, 
        "note_type_fields": note_type_fields, 
        "notecard_key_field": notecard_key_field
    }
    mw.addonManager.writeConfig(__name__, config)
    sync_decks()

def remove_remote_deck() -> None:
    """Function to remove a remote deck."""

    # Get the add-on configuration
    config = mw.addonManager.getConfig(__name__)
    if not config:
        config = {"remote-decks": {}}

    remote_decks = config["remote-decks"]

    # Get all deck names
    deck_names = [remote_decks[key]["deck_name"] for key in remote_decks]

    if len(deck_names) == 0:
        showInfo("There are currently no remote decks.")
        return

    # Ask the user to select a deck
    selection, ok_pressed = QInputDialog.getItem(
        mw,
        "Select a Deck to Unlink",
        "Select a deck to unlink:",
        deck_names,
        0,
        False
    )

    # Remove the deck
    if ok_pressed:
        for key in list(remote_decks.keys()):
            if selection == remote_decks[key]["deck_name"]:
                del remote_decks[key]
                break

        # Save the updated configuration
        mw.addonManager.writeConfig(__name__, config)
        showInfo(f"The deck '{selection}' has been unlinked.")
