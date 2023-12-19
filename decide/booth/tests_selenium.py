from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from voting.models import Question, Voting, QuestionOption, Auth
from mixnet.models import Auth

class MultirrQuestionBoothTest(StaticLiveServerTestCase):

    def create_voting(self):
        q = Question(desc='test question multirr')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()

        v = Voting(name='example voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        return v