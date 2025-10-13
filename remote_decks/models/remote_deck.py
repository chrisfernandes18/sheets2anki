class RemoteDeck:
    def __init__(self):
        self.deck_name: str = ""
        self.questions = []
        self.media = []

    def get_media(self):
        return self.media