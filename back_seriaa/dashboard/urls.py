# dashboard/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Головна сторінка
    path('', views.dashboard_home, name='dashboard_home'),
    
    # API ендпоінти
    path('api/teams/goal-difference/', views.TeamsGoalDifferenceAPI.as_view(), 
         name='api_teams_goal_difference'),
    path('api/players/avg-age/', views.AvgPlayerAgeAPI.as_view(), 
         name='api_avg_player_age'),
    path('api/history/wins-by-year/', views.TeamWinsByYearAPI.as_view(), 
         name='api_wins_by_year'),
    path('api/players/top/', views.TopPlayersAPI.as_view(), 
         name='api_top_players'),
    path('api/matches/by-month/', views.MatchesByMonthAPI.as_view(), 
         name='api_matches_by_month'),
    path('api/coaches/by-country/', views.CoachesByCountryAPI.as_view(), 
         name='api_coaches_by_country'),
    
    # Дашборди
    path('plotly/', views.plotly_dashboard, name='plotly_dashboard'),
    path('bokeh/', views.bokeh_dashboard, name='bokeh_dashboard'),
]