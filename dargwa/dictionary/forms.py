from django import forms
from django.utils.translation import get_language, gettext_lazy as _

from .models import ContactMessage, Idiom, MorphemeNumber, MorphemeType, PartOfSpeech
from .widgets import CheckboxSelectMultipleWithSelectAll


class IdiomPosAdminForm(forms.Form):
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


class BaseSearchForm(forms.Form):
    idiom = forms.ModelMultipleChoiceField(
        label=_('Язык/диалект'),
        queryset=Idiom.objects.all(),
        required=False,
        widget=CheckboxSelectMultipleWithSelectAll(),
    )
    pos = forms.ModelMultipleChoiceField(
        label=_('Часть речи'),
        queryset=PartOfSpeech.objects.all().exclude(pos='n/adj'),
        required=False,
        widget=CheckboxSelectMultipleWithSelectAll(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = get_language()
        self.fields['idiom'].choices = [
            (obj.id, obj.rus if lang == 'ru' and obj.rus else obj.idiom)
            for obj in Idiom.objects.all()
        ]
        self.fields['pos'].choices = [
            (obj.id, (obj.name_en or obj.pos) if lang == 'en' else (obj.name_ru or obj.pos))
            for obj in PartOfSpeech.objects.all().exclude(pos='n/adj')
        ]


class SearchForm(BaseSearchForm):
    search_word = forms.CharField(required=False)
    search_meaning = forms.CharField(required=False)

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


class MorphSearchForm(BaseSearchForm):
    morpheme = forms.CharField(required=False, label=_('Морфема'))
    morph_type = forms.ModelMultipleChoiceField(
        label=_('Тип морфемы'),
        queryset=MorphemeType.objects.exclude(morph_type=MorphemeType.root).order_by('morph_type'),
        required=False,
        widget=CheckboxSelectMultipleWithSelectAll(),
    )
    morph_gloss = forms.ModelMultipleChoiceField(
        label=_('Глосса'),
        queryset=MorphemeNumber.gloss(),
        required=False,
        widget=CheckboxSelectMultipleWithSelectAll(),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lang = get_language()
        self.fields['morph_type'].choices = [
            (obj.id, (obj.name_en or obj.morph_type) if lang == 'en' else (obj.name_ru or obj.morph_type))
            for obj in MorphemeType.objects.exclude(morph_type=MorphemeType.root).order_by('morph_type')
        ]
        self.fields['morpheme'].widget.attrs.update({
            'class': "form-control",
        })


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['email', 'subject', 'message']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your@email.com',
                'required': True
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Тема сообщения'),
                'required': True
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': _('Введите ваше сообщение...'),
                'required': True
            })
        }

    # защита от спама
    honeypot = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label=''
    )

    def clean_honeypot(self):
        value = self.cleaned_data.get('honeypot')
        if value:
            raise forms.ValidationError('Spam!')
        return value
