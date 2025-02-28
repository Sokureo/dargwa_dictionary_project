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
    search_type = forms.ChoiceField(
        choices=(
            ('0', u'Искать слово'),
            ('1', u'Искать синонимы'),
            ('2', u'Искать морфемы'),
            # ('3', u'Искать семантическое поле'),
        ),
    )
    idiom = forms.ModelMultipleChoiceField(
        label='Идиом',
        queryset=Idiom.objects.all(),
        initial=Idiom.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': "form-control"}),
    )
    pos = forms.ModelMultipleChoiceField(
        label='Часть речи',
        queryset=PartOfSpeech.objects.all(),
        initial=PartOfSpeech.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': "form-control"}),
    )
    morph_type = forms.ModelMultipleChoiceField(
        label=_('Тип морфемы'),
        queryset=MorphemeType.objects.exclude(morph_type=MorphemeType.root).order_by('morph_type'),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': "form-control"}),
    )
    morph_gloss = forms.ModelMultipleChoiceField(
        label=_('Глосса'),
        queryset=MorphemeNumber.gloss(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': "form-control"}),
    )
    morpheme = forms.CharField(required=False, label=_('Морфема'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_word'].widget.attrs.update({
            'class': "form-control",
            'placeholder': _('Русский, английский или даргинский'),
        })
        self.fields['search_type'].widget.attrs.update({
            'class': "form-control",
        })
        self.fields['morpheme'].widget.attrs.update({
            'class': "form-control",
        })


# class ContactForm(forms.Form):
#     email = forms.EmailField(label='')
#     message_subject = forms.CharField(label='')
#     message_text = forms.CharField(label='', widget=forms.Textarea)
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['email'].widget.attrs.update({
#             'placeholder': _('Ваш адрес электронной почты'),
#         })
#         self.fields['message_subject'].widget.attrs.update({
#             'placeholder': _('Тема письма'),
#         })
#         self.fields['message_text'].widget.attrs.update({
#             'placeholder': _('Напишите ваше сообщение'),
#         })
