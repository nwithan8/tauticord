class StatLibrary:
    """
    Represents a content library to retrieve stats for.
    """
    def __init__(self, library_name: str, voice_channel_id: int = 0):
        self.library_name = library_name
        self.voice_channel_id = voice_channel_id

