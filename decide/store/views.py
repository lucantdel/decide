from django.utils import timezone
from django.utils.dateparse import parse_datetime
import django_filters.rest_framework
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics

from .models import Vote
from .serializers import VoteSerializer
from base import mods
from base.perms import UserIsStaff

def classic_store(request):
  """ 
    * voting: id
    * voter: id
    * vote: { "a": int, "b": int }
    * voting_type: "classic"
  """
  vid = request.data.get('voting')
  voting = mods.get('voting', params={'id': vid})
  if not voting or not isinstance(voting, list):
      return status.HTTP_401_UNAUTHORIZED
  start_date = voting[0].get('start_date', None)
  end_date = voting[0].get('end_date', None)
  not_started = not start_date or timezone.now() < parse_datetime(start_date)
  is_closed = end_date and parse_datetime(end_date) < timezone.now()
  if not_started or is_closed:
      return status.HTTP_401_UNAUTHORIZED
  uid = request.data.get('voter')
  vote = request.data.get('vote')
  if not vid or not uid or not vote:
      return status.HTTP_400_BAD_REQUEST
    # validating voter
  if request.auth:
      token = request.auth.key
  else:
      token = "NO-AUTH-VOTE"
  voter = mods.post('authentication', entry_point='/getuser/', json={'token': token})
  voter_id = voter.get('id', None)
  if not voter_id or voter_id != uid:
      return status.HTTP_401_UNAUTHORIZED
    # the user is in the census
  perms = mods.get('census/{}'.format(vid), params={'voter_id': uid}, response=True)
  if perms.status_code == 401:
      return status.HTTP_401_UNAUTHORIZED

  a = vote.get("a")

  b = vote.get("b")
  defs = { "a": a, "b": b }
  v, _ = Vote.objects.get_or_create(voting_id=vid, voter_id=uid,
                                    defaults=defs)
  v.a = a
  v.b = b
  v.save()
  return status.HTTP_200_OK


def choices_store(request):
  """ 
    * voting: id
    * voter: id
    * votes: list<{ "a": int, "b": int }>
    * voting_type: "choices"
  """
  vid = request.data.get('voting')
  voting = mods.get('voting', params={'id': vid})
  if not voting or not isinstance(voting, list):
      return status.HTTP_401_UNAUTHORIZED
  start_date = voting[0].get('start_date', None)
  end_date = voting[0].get('end_date', None)
  not_started = not start_date or timezone.now() < parse_datetime(start_date)
  is_closed = end_date and parse_datetime(end_date) < timezone.now()
  if not_started or is_closed:
      return status.HTTP_401_UNAUTHORIZED
  uid = request.data.get('voter')
  votes = request.data.get('votes')
  if not vid or not uid or not votes:
      return status.HTTP_400_BAD_REQUEST
    # validating voter
  if request.auth:
      token = request.auth.key
  else:
      token = "NO-AUTH-VOTE"
  voter = mods.post('authentication', entry_point='/getuser/', json={'token': token})
  voter_id = voter.get('id', None)
  if not voter_id or voter_id != uid:
      return status.HTTP_401_UNAUTHORIZED
    # the user is in the census
  perms = mods.get('census/{}'.format(vid), params={'voter_id': uid}, response=True)
  if perms.status_code == 401:
      return status.HTTP_401_UNAUTHORIZED
  vote = Vote.objects.filter(voter_id=uid, voting_id=vid).first()
  if vote is not None:
      Vote.objects.filter(voter_id=uid, voting_id=vid).delete()
  for v in votes:
    a = v.get("a")
    b = v.get("b")
    defs = { "a": a, "b": b }
    voteDB, _ = Vote.objects.get_or_create(voting_id=vid, voter_id=uid, a=a, b=b, defaults=defs)
    voteDB.a = a
    voteDB.b = b
    voteDB.save()
  return status.HTTP_200_OK


VOTING_TYPES = {
  'choices': choices_store,
  'classic': classic_store,
}

class StoreView(generics.ListAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_fields = ('voting_id', 'voter_id')
    def get(self, request):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        return super().get(request)

    def post(self, request):
        voting_type = request.data.get('voting_type')
        if voting_type not in VOTING_TYPES.keys():
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        status_code = VOTING_TYPES[voting_type](request)
        return  Response({}, status=status_code)