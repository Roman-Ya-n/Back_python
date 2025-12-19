from .base_repository import BaseRepository
from main.models import Match

class MatchRepository(BaseRepository):
    def __init__(self):
        super().__init__(Match)

