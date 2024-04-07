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


class SearchForm(forms.Form):
    search_word = forms.CharField()
    search_type = forms.ChoiceField(
        choices=(
            ('0', u'Искать слово/перевод'),
            ('1', u'Искать синонимы'),
            ('2', u'Искать когнаты'),
        ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_word'].widget.attrs.update({
            'placeholder': _('Русский, английский или даргинский'),
        })
        pos = PartOfSpeech.objects.all()
        self.fields['pos'] = forms.ModelMultipleChoiceField(
            label='Часть речи',
            queryset=pos,
            initial=pos,
            widget=forms.CheckboxSelectMultiple(
                attrs={
                    'size': pos.count(),
                    'style': 'height:auto !important;',
                    'placeholder': 'Все идиомы',
                }
            ),
        )
        idioms = Idiom.objects.all()
        self.fields['idiom'] = forms.ModelMultipleChoiceField(
            label='Идиом',
            queryset=idioms,
            initial=idioms,
            widget=forms.CheckboxSelectMultiple(
                attrs={
                    'size': idioms.count(),
                    'style': 'height:auto !important;',
                }
            ),
        )


class ContactForm(forms.Form):
    message_subject = forms.CharField()
    message_text = forms.CharField(widget=forms.Textarea)
    sender_email = forms.EmailField()
