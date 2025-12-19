from .base_repository import BaseRepository
from main.models import History

class HistoryRepository(BaseRepository):
    def __init__(self):
        super().__init__(History)