import csv
from typing import Union

import requests

from .models.remote_deck import RemoteDeck


def get_remote_deck(
    url: str, note_type_name: str, note_type_fields: list[str] = []
) -> RemoteDeck:
    """Fetches and parses a remote deck from a CSV URL.

    Args:
        url (str): The URL of the CSV file.
        note_type_name (str): The name of the note type.
        note_type_fields (list[str], optional): List of fields in the note type. Defaults to [].
    Returns:
        RemoteDeck: The parsed remote deck.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_data = response.content.decode("utf-8")
    except Exception as e:
        raise Exception(f"Error downloading or reading the CSV: {e}")

    data = parse_csv_data(csv_data)
    remote_deck = build_remote_deck_from_csv(data, note_type_name, note_type_fields)
    return remote_deck


def parse_csv_data(csv_data: Union[str, any]) -> list[list[str]]:
    """Parses CSV data from a string.

    Args:
        csv_data (str or any): The CSV data as a string.
    Returns:
        list[list[str]]: Parsed CSV data as a list of rows, each row being a list of strings.
    """
    print("Parsing CSV data...")  # Debug message
    reader = csv.reader(csv_data.splitlines())
    data = list(reader)
    return data


def build_remote_deck_from_csv(
    data: list[list[str]], note_type_name: str, note_type_fields: list[str]
) -> RemoteDeck:
    """Builds a RemoteDeck object from parsed CSV data.

    Args:
        data (list[list[str]]): Parsed CSV data.
        note_type_name (str): The name of the note type.
        note_type_fields (list[str]): List of fields in the note type.
    Returns:
        RemoteDeck: The constructed RemoteDeck object.
    """
    original_headers = data[0]  # first row of data
    headers = [h.strip() for h in original_headers]
    print("Headers:", headers)  # Debug message

    if set(headers) != set([x.strip() for x in note_type_fields]):
        print("Warning: CSV headers do not match note type fields.")  # Debug message
        print("Note type fields:", note_type_fields)  # Debug message
        raise Exception(
            f"CSV headers do not match note type fields.\nheaders:{original_headers}\nrequired note type fields:{note_type_fields}"
        )

    header_indices = {header: idx for idx, header in enumerate(headers)}

    for field_name, idx in header_indices.items():
        print(f"Header '{field_name}' found at index {idx}")  # Debug message

    notecards = []
    for row_num, row in enumerate(data[1:], start=2):  # Start at line 2 (after headers)
        print(f"Processing row {row_num}: {row}")  # Debug message

        # Skip empty rows
        if not any(cell.strip() for cell in row):
            print(f"Row {row_num} skipped because it is empty")
            continue

        fields = {}
        for field_name, idx in header_indices.items():
            try:
                fields[field_name] = row[idx].strip() if idx < len(row) else ""
            except IndexError:
                print(f"Row {row_num} skipped due to field {field_name}")
                continue

        # Get tags if available
        tags = []
        # tag_text = ''
        # if tag_index is not None and tag_index < len(row):
        #     tag_text = row[tag_index].strip()
        # tags = tag_text.split('::') if tag_text else []
        # tags = [tag.strip() for tag in tags if tag.strip()]

        # Create note card dictionary
        notecard = {"type": note_type_name, "fields": fields, "tags": tags}
        notecards.append(notecard)
        print(f"Added notecard: {notecard['fields']}")  # Debug message

    remote_deck = RemoteDeck()
    remote_deck.deck_name = "Deck from CSV"
    remote_deck.notecards = notecards

    print(f"Total questions added: {len(notecards)}")  # Debug message

    return remote_deck
