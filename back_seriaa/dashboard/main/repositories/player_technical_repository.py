from .base_repository import BaseRepository
from main.models import PlayerTechnical

class PlayerTechnicalRepository(BaseRepository):
    def __init__(self):
        super().__init__(PlayerTechnical)