# main/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    Team, Coach, Stadium, Calendar, 
    History, Match, PlayerDetailed, PlayerTechnical
)
from .serializers import (
    TeamBaseSerializer, TeamDetailSerializer, TeamCreateSerializer,
    CoachBaseSerializer, CoachDetailSerializer, CoachCreateSerializer,
    StadiumBaseSerializer, StadiumDetailSerializer, StadiumCreateSerializer,
    CalendarBaseSerializer, CalendarDetailSerializer, CalendarCreateSerializer,
    HistoryBaseSerializer, HistoryDetailSerializer, HistoryCreateSerializer,
    MatchBaseSerializer, MatchDetailSerializer, MatchCreateSerializer,
    PlayerDetailedBaseSerializer, PlayerDetailedDetailSerializer, PlayerDetailedCreateSerializer,
    PlayerTechnicalBaseSerializer, PlayerTechnicalDetailSerializer, PlayerTechnicalCreateSerializer
)

from .repositories.team_repository import TeamRepository
from .repositories.coach_repository import CoachRepository
from .repositories.stadium_repository import StadiumRepository
from .repositories.calendar_repository import CalendarRepository
from .repositories.history_repository import HistoryRepository
from .repositories.match_repository import MatchRepository
from .repositories.player_detailed_repository import PlayerDetailedRepository
from .repositories.player_technical_repository import PlayerTechnicalRepository

# main/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

class BaseViewSet(viewsets.ModelViewSet):
    
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    
    # These should be defined in child classes
    base_serializer_class = None
    detail_serializer_class = None  
    create_serializer_class = None
    repository_class = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.repository_class:
            self.repo = self.repository_class()
        else:
            raise ValueError("repository_class must be defined in child class")
    
    def get_serializer_class(self):
        if self.action == 'list':
            return self.base_serializer_class
        elif self.action == 'retrieve':
            return self.detail_serializer_class
        elif self.action in ['create', 'update', 'partial_update']:
            return self.create_serializer_class
        return self.base_serializer_class

    def get_queryset(self):
        return self.repo.get_all()

    def retrieve(self, request, pk=None):
        item = self.repo.get_by_id(pk)
        if not item:
            return Response({"error": "Item not found"}, status=404)
        serializer = self.get_serializer(item)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            item = self.repo.create(**serializer.validated_data)
            return Response(self.base_serializer_class(item).data, status=201)
        return Response(serializer.errors, status=400)

    def update(self, request, pk=None):
        item = self.repo.get_by_id(pk)
        if not item:
            return Response({"error": "Item not found"}, status=404)
        
        serializer = self.get_serializer(item, data=request.data)
        if serializer.is_valid():
            updated_item = self.repo.update(pk, serializer.validated_data)
            return Response(self.base_serializer_class(updated_item).data)
        return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        success = self.repo.delete(pk)
        if not success:
            return Response({"error": "Item not found"}, status=404)
        return Response(status=204)
    
# Team ViewSet
class TeamViewSet(BaseViewSet):
    base_serializer_class = TeamBaseSerializer
    detail_serializer_class = TeamDetailSerializer
    create_serializer_class = TeamCreateSerializer
    repository_class = TeamRepository
    queryset = Team.objects.all()

# Coach ViewSet  
class CoachViewSet(BaseViewSet):
    base_serializer_class = CoachBaseSerializer
    detail_serializer_class = CoachDetailSerializer
    create_serializer_class = CoachCreateSerializer
    repository_class = CoachRepository
    queryset = Coach.objects.all()  

# Stadium ViewSet
class StadiumViewSet(BaseViewSet):
    base_serializer_class = StadiumBaseSerializer
    detail_serializer_class = StadiumDetailSerializer
    create_serializer_class = StadiumCreateSerializer
    repository_class = StadiumRepository
    queryset = Stadium.objects.all()  

# Calendar ViewSet
class CalendarViewSet(BaseViewSet):
    base_serializer_class = CalendarBaseSerializer
    detail_serializer_class = CalendarDetailSerializer
    create_serializer_class = CalendarCreateSerializer
    repository_class = CalendarRepository
    queryset = Calendar.objects.all()  

# History ViewSet
class HistoryViewSet(BaseViewSet):
    base_serializer_class = HistoryBaseSerializer
    detail_serializer_class = HistoryDetailSerializer
    create_serializer_class = HistoryCreateSerializer
    repository_class = HistoryRepository
    queryset = History.objects.all()  

# Match ViewSet
class MatchViewSet(BaseViewSet):
    base_serializer_class = MatchBaseSerializer
    detail_serializer_class = MatchDetailSerializer
    create_serializer_class = MatchCreateSerializer
    repository_class = MatchRepository
    queryset = Match.objects.all()  

# PlayerDetailed ViewSet
class PlayerDetailedViewSet(BaseViewSet):
    base_serializer_class = PlayerDetailedBaseSerializer
    detail_serializer_class = PlayerDetailedDetailSerializer
    create_serializer_class = PlayerDetailedCreateSerializer
    repository_class = PlayerDetailedRepository
    queryset = PlayerDetailed.objects.all()  

# PlayerTechnical ViewSet
class PlayerTechnicalViewSet(BaseViewSet):
    base_serializer_class = PlayerTechnicalBaseSerializer
    detail_serializer_class = PlayerTechnicalDetailSerializer
    create_serializer_class = PlayerTechnicalCreateSerializer
    repository_class = PlayerTechnicalRepository
    queryset = PlayerTechnical.objects.all()  

class ReportViewSet(viewsets.ViewSet):
    
    queryset = Team.objects.all()
    
    def list(self, request):
        return Response({
            "message": "Використовуй /api/report/simple-stats/ для звіту",
            "available_actions": ["simple-stats"]
        })
    
    @action(detail=False, methods=['get'])
    def simple_stats(self, request):
        """Найпростіший звіт тільки з кількістю записів"""
        repos = {
            'teams': TeamRepository(),
            'coaches': CoachRepository(),
            'stadiums': StadiumRepository(), 
            'players': PlayerTechnicalRepository(),
            'matches': MatchRepository()
        }
        
        report = {
            "summary": {
                entity: repo.get_all().count()
                for entity, repo in repos.items()
            },
            "total_records": sum(repo.get_all().count() for repo in repos.values())
        }
        return Response(report)