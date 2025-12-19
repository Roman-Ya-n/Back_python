from .base_repository import BaseRepository
from main.models import Calendar

class CalendarRepository(BaseRepository):
    def __init__(self):
        super().__init__(Calendar)