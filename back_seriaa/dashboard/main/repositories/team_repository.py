from .base_repository import BaseRepository
from main.models import Team

class TeamRepository(BaseRepository):
    def __init__(self):
        super().__init__(Team)