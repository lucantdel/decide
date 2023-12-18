from rest_framework import serializers

from .models import Question, QuestionOption, Voting
from base.serializers import KeySerializer, AuthSerializer


class QuestionOptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('number', 'option')


class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    options = serializers.SerializerMethodField()
    def get_options(self, instance):
        if instance.type == 'C':
            serializer = QuestionOptionSerializer(instance.options.all(), many=True).data
        elif instance.type == 'M':
            serializer = QuestionOptionSerializer(instance.options.all(), many=True).data
        return serializer

    class Meta:
        model = Question
        fields = ('desc', 'options', 'type')


class VotingSerializer(serializers.HyperlinkedModelSerializer):
    question = QuestionSerializer(many=False)
    pub_key = KeySerializer()
    auths = AuthSerializer(many=True)

    class Meta:
        model = Voting
        fields = ('id', 'name', 'desc', 'question', 'start_date',
                  'end_date', 'pub_key', 'auths', 'tally', 'postproc')


class SimpleVotingSerializer(serializers.HyperlinkedModelSerializer):
    question = QuestionSerializer(many=False)

    class Meta:
        model = Voting
        fields = ('name', 'desc', 'question', 'start_date', 'end_date')
