from django import forms

class ReuseCensusForm(forms.Form):
    id_to_reuse = forms.IntegerField(label="ID de la votación (Reutilizar)", required=False)
