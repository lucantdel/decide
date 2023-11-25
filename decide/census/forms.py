from django import forms
from .models import Census

class CreationCensusForm(forms.Form):

    voting_id = forms.IntegerField()
    voter_id = forms.IntegerField()

    GENDER = [
        ("MA", "Male"),
        ("FE", "Female"),
        ("NP", "No response")
    ]

    born_date = forms.DateField()
    gender = forms.CharField(max_length=2, choices=GENDER, null=true)
    city = forms.CharField(max_length=20, choices=CITY, null=true)

    class Meta:

        model = Census 
        fields = (
            'voting_id', 
            'voter_id',
            'born_date', 
            'gender', 
            'city'
        )

    def save (self, commit = True):

        census = super(CreationCensusForm, self).save(commit = False)
        census.voting_id= self.cleaned_data['voting_id']
        census.voter_id= self.cleaned_data['voter_id']
        census.born_date= self.cleaned_data['born_date']
        census.gender= self.cleaned_data['gender']
        census.city= self.cleaned_data['city']

        if commit:
            census.save()

        return census