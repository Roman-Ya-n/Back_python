# dashboard/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
import json

from .queries import DashboardQueries
from .serializers import TeamSerializer, PlayerSerializer

class BaseDashboardAPI(APIView):
    """Базовий клас для всіх API ендпоінтів"""
    
    def get_pandas_response(self, queryset):
        """Конвертує QuerySet у pandas DataFrame і повертає JSON"""
        df = DashboardQueries.to_dataframe(queryset)
        
        # Базовий статистичний аналіз
        stats = {}
        if not df.empty:
            numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
            for col in numeric_cols:
                stats[col] = {
                    'mean': float(df[col].mean()),
                    'median': float(df[col].median()),
                    'min': float(df[col].min()),
                    'max': float(df[col].max()),
                    'std': float(df[col].std())
                }
        
        response_data = {
            'data': json.loads(df.to_json(orient='records', date_format='iso')),
            'columns': list(df.columns),
            'shape': df.shape,
            'statistics': stats,
            'info': f"Total records: {len(df)}"
        }
        
        return Response(response_data)


# 1. Ендпоінт для команд з найкращою різницею голів
class TeamsGoalDifferenceAPI(BaseDashboardAPI):
    def get(self, request):
        min_points = request.GET.get('min_points', 50)
        try:
            min_points = int(min_points)
        except ValueError:
            min_points = 50
        
        queryset = DashboardQueries.teams_best_goal_difference(min_points)
        return self.get_pandas_response(queryset)


# 2. Ендпоінт для середнього віку гравців по командах
class AvgPlayerAgeAPI(BaseDashboardAPI):
    def get(self, request):
        queryset = DashboardQueries.avg_player_age_by_team()
        return self.get_pandas_response(queryset)


# 3. Ендпоінт для перемог по роках
class TeamWinsByYearAPI(BaseDashboardAPI):
    def get(self, request):
        team_filter = request.GET.get('team')
        year_from = request.GET.get('year_from')
        year_to = request.GET.get('year_to')
        
        queryset = DashboardQueries.team_wins_by_year()
        
        # Додаємо фільтрацію якщо є параметри
        if team_filter:
            queryset = queryset.filter(win_team__team_name__icontains=team_filter)
        
        if year_from:
            queryset = queryset.filter(year__gte=int(year_from))
        
        if year_to:
            queryset = queryset.filter(year__lte=int(year_to))
            
        return self.get_pandas_response(queryset)


# 4. Ендпоінт для топ гравців
class TopPlayersAPI(BaseDashboardAPI):
    def get(self, request):
        limit = request.GET.get('limit', 10)
        try:
            limit = int(limit)
        except ValueError:
            limit = 10
            
        queryset = DashboardQueries.top_players_by_contributions(limit)
        return self.get_pandas_response(queryset)


# 5. Ендпоінт для матчів по місяцях
class MatchesByMonthAPI(BaseDashboardAPI):
    def get(self, request):
        queryset = DashboardQueries.matches_by_month()
        return self.get_pandas_response(queryset)


# 6. Ендпоінт для тренерів по країнах
class CoachesByCountryAPI(BaseDashboardAPI):
    def get(self, request):
        queryset = DashboardQueries.coaches_by_country()
        return self.get_pandas_response(queryset)


# View для головної сторінки дашборду
def dashboard_home(request):
    """Головна сторінка дашборду"""
    return render(request, 'dashboard/index.html')


# View для Plotly дашборду
def plotly_dashboard(request):
    """Сторінка з Plotly графіками"""
    return render(request, 'dashboard/plotly_dashboard.html')


# View для Bokeh дашборду
def bokeh_dashboard(request):
    """Сторінка з Bokeh графіками"""
    return render(request, 'dashboard/bokeh_dashboard.html')
