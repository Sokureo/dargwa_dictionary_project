from django import forms
from django.utils.translation import gettext_lazy as _

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


class SearchForm(IdiomPosForm):
    search_word = forms.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_word'].widget.attrs.update({
            'placeholder': _('Русский, английский или даргинский'),
        })


class ContactForm(forms.Form):
    message_subject = forms.CharField()
    message_text = forms.TextInput()
    sender_email = forms.EmailInput()
