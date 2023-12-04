from django.contrib import admin

from .models import Census

from django.contrib import messages
from django.contrib.admin.helpers import ActionForm
from django import forms


class ReuseActionForm(ActionForm):
    id_to_reuse = forms.IntegerField(required=False)
    id_to_reuse.label = "ID de la votación (Reutilizar):"


class CensusAdmin(admin.ModelAdmin):
    list_display = ("voting_id", "voter_id")
    list_filter = ("voting_id",)
    search_fields = ("voter_id",)

    def reuse_action(modeladmin, request, queryset):
        reuse_voting_id = request.POST.get("id_to_reuse")

        if reuse_voting_id is not None and reuse_voting_id.strip():
            modeladmin.message_user(request, f"ID introducido: {reuse_voting_id}")

            for census in queryset.all():
                if Census.objects.filter(
                    voting_id=reuse_voting_id, voter_id=census.voter_id
                ).exists():
                    messages.error(
                        request,
                        f"Ya existe Censo con voter_id {census.voter_id} y voting_id {reuse_voting_id} en la base de datos.",
                    )
                    continue  # Salta al siguiente censo en lugar de intentar guardarlo
                re_census = Census()
                re_census.voter_id = census.voter_id
                re_census.voting_id = reuse_voting_id
                re_census.save()
        else:
            messages.error(
                request,
                "Error: Formulario no válido. Asegúrate de ingresar un ID válido.",
            )

    reuse_action.short_description = "Reutilizar Censo"

    actions = [reuse_action]
    action_form = ReuseActionForm


admin.site.register(Census, CensusAdmin)
