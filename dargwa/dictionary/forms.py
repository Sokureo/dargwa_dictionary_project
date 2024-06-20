from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Idiom, MorphemeNumber, MorphemeType, PartOfSpeech


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
    pos = forms.ChoiceField(
        label='Часть речи',
        choices=[
            ('', 'Все части речи'),
            ('n', 'nouns'),
            ('v', 'verbs'),
            ('other', 'other'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'style': 'margin: 10px;'
        })
    )


class SearchForm(forms.Form):
    search_word = forms.CharField(required=False)
    morph_type = forms.ModelMultipleChoiceField(
        label=_('Тип морфемы'),
        queryset=MorphemeType.objects.exclude(morph_type=MorphemeType.root()).order_by('morph_type'),
        required=False,
        widget=forms.SelectMultiple(),
    )
    morph_gloss = forms.ModelMultipleChoiceField(
        label=_('Глосса'),
        queryset=MorphemeNumber.gloss(),
        required=False,
        widget=forms.SelectMultiple(),
    )
    morpheme = forms.CharField(required=False)
    # morpheme = forms.ModelChoiceField(
    #     label=_('Морфема'),
    #     queryset=Morpheme.objects.all().order_by('morpheme').distinct(),
    #     required=False,
    #     widget=forms.Select(),
    # )
    search_type = forms.ChoiceField(
        choices=(
            ('0', u'Искать слово'),
            ('1', u'Искать синонимы'),
            ('2', u'Искать морфемы'),
            # ('3', u'Искать семантическое поле'),
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
