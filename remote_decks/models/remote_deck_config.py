class RemoteDeckConfig:
    def __init__(self):
        self.url: str = ""
        self.deck_name: str = ""
        self.note_type: str = ""
        self.note_type_fields: list[str] = []
        self.notecard_key_field: str = ""
