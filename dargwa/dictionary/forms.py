from django import forms

from .models import Idiom, PartOfSpeech


class IdiomPosForm(forms.Form):
    idiom = forms.ModelChoiceField(
        label='Идиом',
        queryset=Idiom.objects.all(),
        empty_label='Все идиомы',
        required=False,
        widget=forms.Select(attrs={
            'style': 'margin: 10px;'
        })
    )
    pos = forms.ModelChoiceField(
        label='Часть речи',
        queryset=PartOfSpeech.objects.all(),
        empty_label='Все части речи',
        required=False,
        widget=forms.Select(attrs={
            'style': 'margin: 10px;'
        })
    )
