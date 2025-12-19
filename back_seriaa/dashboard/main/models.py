from django.db import models

from django.db import models

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=100, unique=True)
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    loses = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    goal_difference = models.IntegerField(default=0)

    class Meta:
        db_table = 'Teams'

    def __str__(self):
        return self.team_name


class Coach(models.Model):
    coach_id = models.AutoField(primary_key=True)
    coach_name = models.CharField(max_length=100, null=True)
    experience = models.IntegerField(default=0)
    coach_country = models.CharField(max_length=2, null=True)

    class Meta:
        db_table = 'coach'

    def __str__(self):
        return self.coach_name or "Unknown Coach"


class Stadium(models.Model):
    stadium_id = models.AutoField(primary_key=True)
    stadium_name = models.CharField(max_length=100, null=True)
    stadium_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    capacity = models.IntegerField(null=True)
    city = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'stadium'

    def __str__(self):
        return self.stadium_name or "Unnamed Stadium"


class Calendar(models.Model):
    event_id = models.AutoField(primary_key=True)
    event_date = models.DateField()
    event_stadium = models.ForeignKey(Stadium, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'calendar'

    def __str__(self):
        return f"{self.event_date} ({self.event_stadium})"


class History(models.Model):
    year = models.IntegerField(primary_key=True)
    win_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    win_coach = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'history'

    def __str__(self):
        return f"Year {self.year}: {self.win_team} ({self.win_coach})"


class Match(models.Model):
    match_id = models.IntegerField(primary_key=True)
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    home_team_score = models.IntegerField(default=0)
    away_team_score = models.IntegerField(default=0)

    class Meta:
        db_table = 'matches'

    def __str__(self):
        return f"{self.home_team} vs {self.away_team}"


class PlayerDetailed(models.Model):
    player_detailed_id = models.IntegerField(primary_key=True)
    player_physic = models.IntegerField(null=True)
    player_country = models.CharField(max_length=2, null=True)
    player_age = models.IntegerField(null=True)
    player_foot = models.CharField(max_length=5, choices=[
        ('left', 'Left'),
        ('right', 'Right'),
        ('both', 'Both'),
    ], default='right')

    class Meta:
        db_table = 'players_detailed'

    def __str__(self):
        return f"{self.player_country} ({self.player_foot})"


class PlayerTechnical(models.Model):
    player_id = models.AutoField(primary_key=True)
    player_name = models.CharField(max_length=255)
    player_team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    position = models.CharField(max_length=50, null=True)
    goal_scored = models.IntegerField(default=0)
    assist_scored = models.IntegerField(default=0)

    class Meta:
        db_table = 'players_technical'

    def __str__(self):
        return self.player_name

