import json

from base import mods
from census.models import Census
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView
from voting.models import Voting
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


def index(request):
    votaciones = Voting.objects.order_by("name")
    return render(request, "index.html", {"votaciones": votaciones})

def obtener_detalle_votacion(request, votacion_id):
    voting = get_object_or_404(Voting, pk=votacion_id)  
    booth_url = f"http://localhost:8000/booth/vote/{votacion_id}/"  # Reemplaza con la URL correcta
    response = HttpResponse(status=302)
    response["Location"] = booth_url
    return response


@login_required(login_url="/signin")
def voting_list(request):
    votings_ids = Census.objects.filter(voter_id=request.user.id).values_list(
        "voting_id", flat=True
    )
    user_votings = Voting.objects.filter(id__in=votings_ids, start_date__isnull=False)

    user_votings = user_votings.order_by("-end_date")

    return render(request, "booth/voting-list.html", {"user_votings": user_votings})


class BoothView(TemplateView):
    template_name = "booth/booth.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vid = kwargs.get("voting_id", 0)

        try:
            r = mods.get("voting", params={"id": vid})
            # Casting numbers to string to manage in javascript with BigInt
            # and avoid problems with js and big number conversion
            for k, v in r[0]["pub_key"].items():
                r[0]["pub_key"][k] = str(v)

            context["voting"] = json.dumps(r[0])
        except:
            raise Http404

        context["KEYBITS"] = settings.KEYBITS

        return context