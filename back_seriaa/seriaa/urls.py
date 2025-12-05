from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from main import views

router = DefaultRouter()
router.register(r'teams', views.TeamViewSet, basename='team')
router.register(r'coach', views.CoachViewSet, basename='coach')
router.register(r'stadium', views.StadiumViewSet, basename='stadium')
router.register(r'calendar', views.CalendarViewSet, basename='calendar')
router.register(r'history', views.HistoryViewSet, basename='history')
router.register(r'match', views.MatchViewSet, basename='match')
router.register(r'player-detailed', views.PlayerDetailedViewSet, basename='player-detailed')
router.register(r'player-technical', views.PlayerTechnicalViewSet, basename='player-technical')
router.register(r'report', views.ReportViewSet, basename='report')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
]
