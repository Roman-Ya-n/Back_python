from django.contrib import admin
from main.models import Team, Coach, Stadium, Calendar, History, Match, PlayerDetailed, PlayerTechnical

admin.site.register(Team)
admin.site.register(Coach)
admin.site.register(Stadium)
admin.site.register(Calendar)
admin.site.register(History)
admin.site.register(Match)
admin.site.register(PlayerDetailed)
admin.site.register(PlayerTechnical)