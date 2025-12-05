# main/serializers.py
from rest_framework import serializers
from .models import (
    Team, Coach, Stadium, Calendar, 
    History, Match, PlayerDetailed, PlayerTechnical
)


# ==================== BASE SERIALIZERS ====================

class TeamBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['team_id', 'team_name', 'points', 'wins', 'loses', 'draws', 'goal_difference']


class CoachBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ['coach_id', 'coach_name', 'experience', 'coach_country']


class StadiumBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stadium
        fields = ['stadium_id', 'stadium_name', 'stadium_team', 'capacity', 'city']

class CalendarCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ['event_date', 'event_stadium']


class HistoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = History
        fields = ['year', 'win_team', 'win_coach']


class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ['match_id', 'home_team', 'away_team', 'home_team_score', 'away_team_score']


class PlayerTechnicalBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerTechnical
        fields = ['player_id', 'player_name', 'player_team', 'position', 'goal_scored', 'assist_scored']


class PlayerDetailedBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerDetailed
        fields = ['player_detailed_id', 'player_physic', 'player_country', 'player_age', 'player_foot']


# ==================== DETAIL SERIALIZERS (WITH RELATED DATA) ====================

class TeamDetailSerializer(serializers.ModelSerializer):
    # Стадіон команди
    stadium = serializers.SerializerMethodField()
    # Гравці команди
    players = serializers.SerializerMethodField()
    # Тренер (шукаємо через історію)
    current_coach = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = [
            'team_id', 'team_name', 'points', 'wins', 'loses', 'draws', 
            'goal_difference', 'stadium', 'players', 'current_coach'
        ]

    def get_stadium(self, obj):
        stadium = Stadium.objects.filter(stadium_team=obj).first()
        if stadium:
            return StadiumBaseSerializer(stadium).data
        return None

    def get_players(self, obj):
        players = PlayerTechnical.objects.filter(player_team=obj)
        return PlayerTechnicalBaseSerializer(players, many=True).data

    def get_current_coach(self, obj):
        # Останній тренер, який виграв з цією командою
        history = History.objects.filter(win_team=obj).order_by('-year').first()
        if history and history.win_coach:
            return CoachBaseSerializer(history.win_coach).data
        return None


class CoachDetailSerializer(serializers.ModelSerializer):
    # Команди, які тренер вигравав
    winning_teams = serializers.SerializerMethodField()
    # Роки перемог
    winning_years = serializers.SerializerMethodField()

    class Meta:
        model = Coach
        fields = [
            'coach_id', 'coach_name', 'experience', 'coach_country',
            'winning_teams', 'winning_years'
        ]

    def get_winning_teams(self, obj):
        winning_teams = History.objects.filter(win_coach=obj).select_related('win_team')
        teams = [history.win_team for history in winning_teams if history.win_team]
        return TeamBaseSerializer(teams, many=True).data

    def get_winning_years(self, obj):
        winning_years = History.objects.filter(win_coach=obj).values_list('year', flat=True)
        return list(winning_years)


class StadiumDetailSerializer(serializers.ModelSerializer):
    # Команда, яка грає на стадіоні
    team = serializers.SerializerMethodField()
    # Матчі на цьому стадіоні
    upcoming_matches = serializers.SerializerMethodField()

    class Meta:
        model = Stadium
        fields = [
            'stadium_id', 'stadium_name', 'stadium_team', 'capacity', 'city',
            'team', 'upcoming_matches'
        ]

    def get_team(self, obj):
        if obj.stadium_team:
            return TeamBaseSerializer(obj.stadium_team).data
        return None

    def get_upcoming_matches(self, obj):
        from django.utils import timezone
        upcoming_matches = Calendar.objects.filter(
            event_stadium=obj,
            event_date__gte=timezone.now()
        ).order_by('event_date')[:5]  # Наступні 5 матчів
        return CalendarBaseSerializer(upcoming_matches, many=True).data


class PlayerTechnicalDetailSerializer(serializers.ModelSerializer):
    # Детальна інформація про гравця
    player_details = serializers.SerializerMethodField()
    # Команда гравця
    team_info = serializers.SerializerMethodField()

    class Meta:
        model = PlayerTechnical
        fields = [
            'player_id', 'player_name', 'player_team', 'position', 
            'goal_scored', 'assist_scored', 'player_details', 'team_info'
        ]

    def get_player_details(self, obj):
        try:
            details = PlayerDetailed.objects.get(player_detailed_id=obj.player_id)
            return PlayerDetailedBaseSerializer(details).data
        except PlayerDetailed.DoesNotExist:
            return None

    def get_team_info(self, obj):
        if obj.player_team:
            return TeamBaseSerializer(obj.player_team).data
        return None


class PlayerDetailedDetailSerializer(serializers.ModelSerializer):
    # Технічна інформація про гравця
    technical_info = serializers.SerializerMethodField()

    class Meta:
        model = PlayerDetailed
        fields = [
            'player_detailed_id', 'player_physic', 'player_country', 
            'player_age', 'player_foot', 'technical_info'
        ]

    def get_technical_info(self, obj):
        try:
            technical = PlayerTechnical.objects.get(player_id=obj.player_detailed_id)
            return PlayerTechnicalBaseSerializer(technical).data
        except PlayerTechnical.DoesNotExist:
            return None


# ==================== CREATE/UPDATE SERIALIZERS ====================

class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['team_name', 'points', 'wins', 'loses', 'draws', 'goal_difference']

    def validate_team_name(self, value):
        if Team.objects.filter(team_name__iexact=value).exists():
            raise serializers.ValidationError("Команда з такою назвою вже існує")
        return value

    def validate(self, data):
        # Перевірка, щоб кількість перемог+програшів+нічиїх не перевищувала загальну кількість ігор
        wins = data.get('wins', 0)
        loses = data.get('loses', 0)
        draws = data.get('draws', 0)
        
        if wins < 0 or loses < 0 or draws < 0:
            raise serializers.ValidationError("Кількість перемог, поразок і нічиїх не може бути від'ємною")
        
        return data


class CoachCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ['coach_name', 'experience', 'coach_country']

    def validate_experience(self, value):
        if value < 0:
            raise serializers.ValidationError("Досвід не може бути від'ємним")
        return value

    def validate_coach_country(self, value):
        if value and len(value) != 2:
            raise serializers.ValidationError("Код країни має складатися з 2 символів")
        return value


class StadiumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stadium
        fields = ['stadium_name', 'stadium_team', 'capacity', 'city']

    def validate_capacity(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Місткість не може бути від'ємною")
        return value


class PlayerTechnicalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerTechnical
        fields = ['player_name', 'player_team', 'position', 'goal_scored', 'assist_scored']

    def validate_goal_scored(self, value):
        if value < 0:
            raise serializers.ValidationError("Кількість голів не може бути від'ємною")
        return value

    def validate_assist_scored(self, value):
        if value < 0:
            raise serializers.ValidationError("Кількість асистів не може бути від'ємною")
        return value


class PlayerDetailedCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerDetailed
        fields = ['player_detailed_id', 'player_physic', 'player_country', 'player_age', 'player_foot']

    def validate_player_age(self, value):
        if value and (value < 16 or value > 50):
            raise serializers.ValidationError("Вік гравця має бути від 16 до 50 років")
        return value

    def validate_player_physic(self, value):
        if value and (value < 1 or value > 100):
            raise serializers.ValidationError("Фізична форма має бути від 1 до 100")
        return value


# ==================== MATCH & CALENDAR SERIALIZERS ====================

class MatchBaseSerializer(serializers.ModelSerializer):
    home_team_name = serializers.CharField(source='home_team.team_name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.team_name', read_only=True)

    class Meta:
        model = Match
        fields = [
            'match_id', 'home_team', 'away_team', 'home_team_name', 'away_team_name',
            'home_team_score', 'away_team_score'
        ]


class MatchDetailSerializer(serializers.ModelSerializer):
    home_team_info = serializers.SerializerMethodField()
    away_team_info = serializers.SerializerMethodField()
    match_result = serializers.SerializerMethodField()

    class Meta:
        model = Match
        fields = [
            'match_id', 'home_team', 'away_team', 'home_team_score', 'away_team_score',
            'home_team_info', 'away_team_info', 'match_result'
        ]

    def get_home_team_info(self, obj):
        return TeamBaseSerializer(obj.home_team).data

    def get_away_team_info(self, obj):
        return TeamBaseSerializer(obj.away_team).data

    def get_match_result(self, obj):
        if obj.home_team_score > obj.away_team_score:
            return f"Перемога {obj.home_team.team_name}"
        elif obj.home_team_score < obj.away_team_score:
            return f"Перемога {obj.away_team.team_name}"
        else:
            return "Нічия"


class CalendarBaseSerializer(serializers.ModelSerializer):
    stadium_name = serializers.CharField(source='event_stadium.stadium_name', read_only=True)
    stadium_city = serializers.CharField(source='event_stadium.city', read_only=True)

    class Meta:
        model = Calendar
        fields = ['event_id', 'event_date', 'event_stadium', 'stadium_name', 'stadium_city']


class CalendarDetailSerializer(serializers.ModelSerializer):
    stadium_info = serializers.SerializerMethodField()
    matches_on_date = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = ['event_id', 'event_date', 'event_stadium', 'stadium_info', 'matches_on_date']

    def get_stadium_info(self, obj):
        if obj.event_stadium:
            return StadiumBaseSerializer(obj.event_stadium).data
        return None

    def get_matches_on_date(self, obj):
        # Матчі, заплановані на цю дату (можна додати логіку зв'язку з Match)
        return []  # Поки що пустий список - можна розширити


class HistoryBaseSerializer(serializers.ModelSerializer):
    win_team_name = serializers.CharField(source='win_team.team_name', read_only=True)
    win_coach_name = serializers.CharField(source='win_coach.coach_name', read_only=True)

    class Meta:
        model = History
        fields = ['year', 'win_team', 'win_coach', 'win_team_name', 'win_coach_name']


class HistoryDetailSerializer(serializers.ModelSerializer):
    winning_team = serializers.SerializerMethodField()
    winning_coach = serializers.SerializerMethodField()

    class Meta:
        model = History
        fields = ['year', 'win_team', 'win_coach', 'winning_team', 'winning_coach']

    def get_winning_team(self, obj):
        if obj.win_team:
            return TeamBaseSerializer(obj.win_team).data
        return None

    def get_winning_coach(self, obj):
        if obj.win_coach:
            return CoachBaseSerializer(obj.win_coach).data
        return None


# ==================== REPORT SERIALIZERS ====================

class TeamStatsSerializer(serializers.Serializer):
    team_id = serializers.IntegerField()
    team_name = serializers.CharField()
    total_matches = serializers.IntegerField()
    total_goals_scored = serializers.IntegerField()
    total_goals_conceded = serializers.IntegerField()
    win_percentage = serializers.FloatField()


class PlayerStatsSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    player_name = serializers.CharField()
    team_name = serializers.CharField()
    total_goals = serializers.IntegerField()
    total_assists = serializers.IntegerField()
    goal_contribution = serializers.IntegerField()


# ==================== SERIALIZER FOR NESTED RELATIONS ====================

class TeamWithPlayersSerializer(serializers.ModelSerializer):
    players = PlayerTechnicalBaseSerializer(many=True, read_only=True, source='playertechnical_set')

    class Meta:
        model = Team
        fields = ['team_id', 'team_name', 'points', 'players']


class StadiumWithTeamSerializer(serializers.ModelSerializer):
    team = TeamBaseSerializer(read_only=True, source='stadium_team')

    class Meta:
        model = Stadium
        fields = ['stadium_id', 'stadium_name', 'capacity', 'city', 'team']