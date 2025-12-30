# dashboard/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
import json

from .queries import DashboardQueries

from bokeh.resources import CDN


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
    return render(request, 'index.html')


# dashboard/views.py
from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response

# Додайте ці імпорти
from .utils import PlotlyCharts, BokehCharts
from bokeh.embed import components
from bokeh.resources import CDN

def plotly_dashboard(request):
    
    # Генеруємо всі 6 графіків
    plotly_chart1 = PlotlyCharts.create_teams_bar_chart()
    plotly_chart2 = PlotlyCharts.create_age_pie_chart()
    plotly_chart3 = PlotlyCharts.create_wins_line_chart()
    plotly_chart4 = PlotlyCharts.create_players_scatter()
    plotly_chart5 = PlotlyCharts.create_matches_area_chart()
    plotly_chart6 = PlotlyCharts.create_coaches_heatmap()
    
    # Передаємо графіки в контекст шаблону
    context = {
        'plotly_chart1': plotly_chart1,
        'plotly_chart2': plotly_chart2,
        'plotly_chart3': plotly_chart3,
        'plotly_chart4': plotly_chart4,
        'plotly_chart5': plotly_chart5,
        'plotly_chart6': plotly_chart6,
    }
    
    return render(request, 'plotly_dashboard.html', context)

def bokeh_dashboard(request):
    """Сторінка з 6 графіками Bokeh"""
    from bokeh.embed import components
    from .utils import BokehCharts
    
    # Перевіряємо кожен графік
    charts = []
    divs = []
    scripts = []
    
    chart_methods = [
        ('teams_bar', BokehCharts.create_teams_bar_chart_bokeh()),
        ('players_goals', BokehCharts.create_players_goals_bokeh()),
        ('stadium_capacity', BokehCharts.create_stadium_capacity_bokeh()),
        ('matches_timeline', BokehCharts.create_matches_timeline_bokeh()),
        ('players_by_country', BokehCharts.create_players_by_country_bokeh()),
        ('team_stats_grid', BokehCharts.create_team_stats_grid_bokeh()),
    ]
    
    for name, chart in chart_methods:
        if chart:
            script, div = components(chart)
            scripts.append(script)
            divs.append(div)
            print(f"DEBUG: Графік {name} створено - div: {bool(div)}, script: {bool(script)}")
        else:
            scripts.append("")
            divs.append(f"<p>Немає даних для {name}</p>")
            print(f"DEBUG: Графік {name} - None")
    
    all_scripts = "".join(scripts)
    
    context = {
        'bokeh_js': all_scripts,
        'bokeh_css': CDN.render_css(),
        'bokeh_chart1': divs[0],
        'bokeh_chart2': divs[1],
        'bokeh_chart3': divs[2],
        'bokeh_chart4': divs[3],
        'bokeh_chart5': divs[4],
        'bokeh_chart6': divs[5],
    }
    
    return render(request, 'bokeh_dashboard.html', context)
