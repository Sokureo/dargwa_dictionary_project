from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Idiom, MorphemeNumber, MorphemeType, PartOfSpeech


class IdiomPosForm(forms.Form):
    idiom = forms.ModelChoiceField(
        label=_('Язык/диалект'),
        queryset=Idiom.objects.all(),
        empty_label=_('Все языки/диалекты'),
        required=False,
        widget=forms.Select(attrs={
            'style': 'margin: 10px;'
        })
    )
    pos = forms.ChoiceField(
        label=_('Часть речи'),
        choices=[
            ('', _('Все части речи')),
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
    search_meaning = forms.CharField(required=False)
    idiom = forms.ModelMultipleChoiceField(
        label=_('Язык/диалект'),
        queryset=Idiom.objects.all(),
        required=False,
        initial=Idiom.objects.all(),
        widget=forms.CheckboxSelectMultiple(),
    )
    pos = forms.ModelMultipleChoiceField(
        label=_('Часть речи'),
        queryset=PartOfSpeech.objects.all().exclude(pos='n/adj'),
        required=False,
        initial=PartOfSpeech.objects.all().exclude(pos='n/adj'),
        widget=forms.SelectMultiple(),
    )
    morph_type = forms.ModelMultipleChoiceField(
        label=_('Тип морфемы'),
        queryset=MorphemeType.objects.exclude(morph_type=MorphemeType.root).order_by('morph_type'),
        required=False,
        widget=forms.SelectMultiple(),
    )
    morph_gloss = forms.ModelMultipleChoiceField(
        label=_('Глосса'),
        queryset=MorphemeNumber.gloss(),
        required=False,
        widget=forms.SelectMultiple(),
    )
    morpheme = forms.CharField(required=False, label=_('Морфема'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['search_word'].widget.attrs.update({
            'class': "form-control",
            'placeholder': _('даргинский'),
        })
        self.fields['search_meaning'].widget.attrs.update({
            'class': "form-control",
            'placeholder': _('русский или английский'),
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
