from django.db.models import Count, Sum, Avg, Max, Min, F, Q
from django.db.models.functions import TruncMonth, ExtractYear
from .models import Team, PlayerTechnical, PlayerDetailed, History, Match, Calendar, Coach
import pandas as pd

class DashboardQueries:
    
    # 1. Команди з найкращою різницею голів (з HAVING)
    @staticmethod
    def teams_best_goal_difference(min_points=50):
        """
        Команди з різницею голів > 20, відсортовані за різницею
        Аналог SQL: SELECT team_name, goal_difference FROM Teams 
                   WHERE points > %s AND goal_difference > 20 
                   ORDER BY goal_difference DESC
        """
        queryset = Team.objects.filter(
            points__gte=min_points,
            goal_difference__gt=20
        ).order_by('-goal_difference').values(
            'team_id', 'team_name', 'points', 'goal_difference'
        )
        return queryset
    
    # 2. Середній вік гравців по командах
    @staticmethod
    def avg_player_age_by_team():
        """
        Групування по командах, середній вік гравців
        """
        queryset = PlayerTechnical.objects.select_related(
            'player_team', 'playerdetailed'
        ).filter(
            playerdetailed__player_age__isnull=False
        ).values(
            'player_team__team_name'
        ).annotate(
            avg_age=Avg('playerdetailed__player_age'),
            player_count=Count('player_id')
        ).order_by('-avg_age')
        return queryset
    
    # 3. Кількість перемог команд по роках
    @staticmethod
    def team_wins_by_year():
        """
        Кількість перемог кожної команди по роках з історії
        """
        queryset = History.objects.filter(
            win_team__isnull=False
        ).values(
            'year', 'win_team__team_name'
        ).annotate(
            win_count=Count('win_team')
        ).order_by('-year', '-win_count')
        return queryset
    
    # 4. Топ-10 гравців за гол+асисти
    @staticmethod
    def top_players_by_contributions(limit=10):
        """
        Топ гравців за сумою голів та асистів
        """
        queryset = PlayerTechnical.objects.annotate(
            total_contributions=F('goal_scored') + F('assist_scored')
        ).order_by('-total_contributions').values(
            'player_name', 'player_team__team_name',
            'goal_scored', 'assist_scored', 'total_contributions'
        )[:limit]
        return queryset
    
    # 5. Розподіл матчів по місяцях
    @staticmethod
    def matches_by_month():
        """
        Кількість матчів по місяцях (з календаря)
        """
        queryset = Calendar.objects.annotate(
            month=TruncMonth('event_date')
        ).values('month').annotate(
            match_count=Count('event_id')
        ).order_by('month')
        return queryset
    
    # 6. Статистика тренерів по країнах
    @staticmethod
    def coaches_by_country():
        """
        Групування тренерів по країнах, середній досвід
        """
        queryset = Coach.objects.filter(
            coach_country__isnull=False
        ).values('coach_country').annotate(
            coach_count=Count('coach_id'),
            avg_experience=Avg('experience'),
            max_experience=Max('experience')
        ).order_by('-coach_count')
        return queryset
    
    # Додатково: конвертація в pandas DataFrame
    @staticmethod
    def to_dataframe(queryset):
        """Конвертує QuerySet у pandas DataFrame"""
        return pd.DataFrame(list(queryset))