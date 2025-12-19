from .base_repository import BaseRepository
from main.models import Coach

class CoachRepository(BaseRepository):
    def __init__(self):
        super().__init__(Coach)