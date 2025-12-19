from .base_repository import BaseRepository
from main.models import Stadium

class StadiumRepository(BaseRepository):
    def __init__(self):
        super().__init__(Stadium)