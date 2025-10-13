import csv
import requests
import re

from typing import Union

from .models.remote_deck import RemoteDeck

def get_remote_deck(url: str, note_type_fields: list[str] = []) -> RemoteDeck:
    """Fetches and parses a remote deck from a CSV URL.
    
    Args:
        url (str): The URL of the CSV file.
        note_type_fields (list[str], optional): List of fields in the note type. Defaults to [].
    Returns:
        RemoteDeck: The parsed remote deck.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_data = response.content.decode('utf-8')
    except Exception as e:
        raise Exception(f"Error downloading or reading the CSV: {e}")

    data = parse_csv_data(csv_data)
    remote_deck = build_remote_deck_from_csv(data)
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

def build_remote_deck_from_csv(data: list[list[str]]) -> RemoteDeck:
    """Builds a RemoteDeck object from parsed CSV data.
    Args:
        data (list[list[str]]): Parsed CSV data.
    Returns:
        RemoteDeck: The constructed RemoteDeck object.
    """

    # Process headers to find indices of 'question', 'answer', and 'tags'
    headers = [h.strip().lower() for h in data[0]]
    print("Headers:", headers)  # Debug message

    question_index = headers.index('question') if 'question' in headers else headers.index('front') if 'front' in headers else 0
    answer_index = headers.index('answer') if 'answer' in headers else headers.index('back') if 'back' in headers else 1
    tag_index = headers.index('tags') if 'tags' in headers else None

    print("Indices - Question:", question_index, "Answer:", answer_index, "Tags:", tag_index)  # Debug message

    questions = []
    for row_num, row in enumerate(data[1:], start=2):  # Start at line 2 (after headers)
        print(f"Processing row {row_num}: {row}")  # Debug message

        # Skip empty rows
        if not any(cell.strip() for cell in row):
            print(f"Row {row_num} skipped because it is empty")
            continue

        # Get question and answer
        try:
            question_text = row[question_index].strip()
            answer_text = row[answer_index].strip()
        except IndexError:
            print(f"Row {row_num} skipped due to missing question or answer")
            continue

        # Get tags if available
        tag_text = ''
        if tag_index is not None and tag_index < len(row):
            tag_text = row[tag_index].strip()
        tags = tag_text.split('::') if tag_text else []
        tags = [tag.strip() for tag in tags if tag.strip()]

        # Detect if it's a Cloze deletion
        if re.search(r'{{c\d+::.*?}}', question_text):
            card_type = 'Cloze'
            fields = {
                'Text': question_text,
                'Extra': answer_text  # The 'Extra' field can be empty
            }
        else:
            card_type = 'Basic'
            fields = {
                'Front': question_text,
                'Back': answer_text
            }

        print(f"Detected card type: {card_type}")  # Debug message

        # Create question dictionary
        question = {
            'type': card_type,
            'fields': fields,
            'tags': tags
        }
        questions.append(question)
        print(f"Added question: {question_text}")  # Debug message

    remote_deck = RemoteDeck()
    remote_deck.deck_name = "Deck from CSV"
    remote_deck.questions = questions  # Keep using 'questions' attribute

    print(f"Total questions added: {len(questions)}")  # Debug message

    return remote_deck
