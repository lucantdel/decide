from django import forms
from .models import Census

class CreationCensusForm(forms.Form):

    voting_id = forms.IntegerField()
    voter_id = forms.IntegerField()

    GENDER_CHOICES = [
        ("MA", "Male"),
        ("FE", "Female"),
        ("NP", "No response")
    ]
    
    CITY_CHOICES = [
        ("SE", "Sevilla"),
        ("MA", "Madrid"),
        ("BAR", "Barcelona"),
        ("VA", "Valencia"),
        ("ZA", "Zaragoza")
    ]

    born_date = forms.DateField()
    gender = forms.ChoiceField(choices=GENDER_CHOICES, required=False)
    city = forms.ChoiceField(choices=CITY_CHOICES, required=False)

    class Meta:
        model = Census 
        fields = (
            'voting_id', 
            'voter_id',
            'born_date', 
            'gender', 
            'city'
        )

    def save(self, commit=True):
        census = super(CreationCensusForm, self).save(commit=False)
        census.voting_id = self.cleaned_data['voting_id']
        census.voter_id = self.cleaned_data['voter_id']
        census.born_date = self.cleaned_data['born_date']
        census.gender = self.cleaned_data['gender']
        census.city = self.cleaned_data['city']

        if commit:
            census.save()

        return census

class ReuseCensusForm(forms.Form):
    id_to_reuse = forms.IntegerField(label="ID de la votación (Reutilizar)", required=False)
