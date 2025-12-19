from .base_repository import BaseRepository
from main.models import PlayerDetailed

class PlayerDetailedRepository(BaseRepository):
    def __init__(self):
        super().__init__(PlayerDetailed)