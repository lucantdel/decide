from django.contrib import admin

from .models import Vote
from .models import VoteByPreference


admin.site.register(Vote)
admin.site.register(VoteByPreference)
