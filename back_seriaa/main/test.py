import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seriaa.settings')
django.setup()

from main.repositories.team_repository import TeamRepository
from main.repositories.coach_repository import CoachRepository

team_repo = TeamRepository()
coach_repo = CoachRepository()

team_repo.update(28, team_name="Updated Team Name")
