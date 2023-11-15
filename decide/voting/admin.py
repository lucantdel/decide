from django.contrib import admin
from django.utils import timezone

from .models import QuestionOption
from .models import Question
from .models import Voting
from .models import QuestionOptionByPreference
from .models import QuestionByPreference
from .models import VotingByPreference

from .filters import StartedFilter


def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get("auth-token", "")
        v.tally_votes(token)


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]


class VotingAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    readonly_fields = ("start_date", "end_date", "pub_key","tally", "postproc")
    date_hierarchy = "start_date"
    list_filter = (StartedFilter,)
    search_fields = ("name", )

    actions = [ start, stop, tally ]


class QuestionOptionByPreferenceInline(admin.TabularInline):
    model = QuestionOptionByPreference


class QuestionByPreferenceAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionByPreferenceInline]

class VotingByPreferenceAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date")
    readonly_fields = ("start_date", "end_date", "pub_key", "tally", "postproc")
    date_hierarchy = "start_date"
    list_filter = (StartedFilter,)
    search_fields = ("name",)

    actions = [start, stop, tally]

admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(VotingByPreference, VotingByPreferenceAdmin)
admin.site.register(QuestionByPreference, QuestionByPreferenceAdmin)