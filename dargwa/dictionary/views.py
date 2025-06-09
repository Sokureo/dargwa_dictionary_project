from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .forms import IdiomPosForm, SearchForm
from .models import Word, WordForm, Morpheme, MorphemeType, MorphemeNumber, PartOfSpeech, Idiom


class StartPageView(TemplateView):
    template_name = 'index.html'
#     success_url = reverse_lazy('dictionary:start_page')
#     success_message = _('Сообщение отправлено!')
#     form_class = ContactForm
#
#     def form_valid(self, form):
#         email = form.cleaned_data.get('email')
#         subject = form.cleaned_data.get('message_subject')
#         message = form.cleaned_data.get('message_text')
#
#         send_mail(
#             subject=subject,
#             message=message,
#             from_email=email,
#             recipient_list=[settings.NOTIFY_EMAIL],
#             fail_silently=False,
#         )
#         messages.success(self.request, message=_('Сообщение отправлено!'))
#         return super(StartPageView, self).form_valid(form)


class SearchView(FormView):
    template_name = 'search.html'
    form_class = SearchForm
    meaning_regex = r'(\(.+\))*(^|[,)]){}([ ,;]|$)'
    meaning_regex2 = r'(\(.+\))*(^|[ ,)]){}([,;]|$)'
    class_regex = "'{}'"

    def post(self, request, *args, **kwargs):
        form = self.get_form()

        if form.is_valid():
            search_word = form.cleaned_data.get('search_word')
            search_type = form.cleaned_data.get('search_type')
            idiom = form.cleaned_data.get('idiom') or Idiom.objects.all().values_list('id', flat=True)
            pos = form.cleaned_data.get('pos') or PartOfSpeech.objects.all().values_list('id', flat=True)
            morph_type = form.cleaned_data.get('morph_type')
            morph_gloss = form.cleaned_data.get('morph_gloss')
            morpheme = form.cleaned_data.get('morpheme')

            q = Q(idiom__in=idiom) & Q(pos__in=pos)
            words = list()
            if search_type == '0':
                if search_word:
                    q &= Q(
                        Q(entry_cyr=search_word) | Q(entry_lat=search_word) |
                        Q(class_words_cyr__iregex=self.class_regex.format(search_word)) |
                        Q(class_words_lat__iregex=self.class_regex.format(search_word))
                    )
                    words = Word.objects.filter(q)
            elif search_type == '1':
                if search_word:
                    q &= Q(
                        Q(meaning_rus__iregex=self.meaning_regex.format(search_word)) |
                        Q(meaning_rus__iregex=self.meaning_regex2.format(search_word)) |
                        Q(meaning_eng__iregex=self.meaning_regex.format(search_word)) |
                        Q(meaning_eng__iregex=self.meaning_regex2.format(search_word))
                    )
                    words = Word.objects.filter(q)
            elif search_type == '2':
                q_morph = Q()
                if morph_type:
                    q_morph = Q(morphemes__morph_type__in=morph_type)
                if morph_gloss:
                    q_morph &= Q(morphemes__morph_number__in=morph_gloss)
                if morpheme:
                    q_morph &= Q(morphemes__morpheme=morpheme)
                if q_morph:
                    words = Word.objects.prefetch_related('morphemes').filter(q_morph)
                    words = words.filter(q)
            return render(
                request,
                'result_list.html',
                {'result_list': words, 'search_params': self.get_used_search_params(form.cleaned_data)}
            )
        else:
            return self.form_invalid(form)

    def get_used_search_params(self, cleaned_data):
        params = dict()
        search_word = cleaned_data.get('search_word')
        search_type = cleaned_data.get('search_type')
        idioms = cleaned_data.get('idiom') or Idiom.objects.all().values_list('id', flat=True)
        poss = cleaned_data.get('pos') or PartOfSpeech.objects.all().values_list('id', flat=True)
        morph_type = cleaned_data.get('morph_type')
        morph_gloss = cleaned_data.get('morph_gloss')
        morpheme = cleaned_data.get('morpheme')

        if search_type:
            if search_type == '0':
                search_name = 'Поиск по даргинскому слову'
            elif search_type == '1':
                search_name = 'Поиск по значению'
            elif search_type == '2':
                search_name = 'Поиск по морфеме'
            params['Тип поиска'] = search_name
        if idioms:
            idioms_list = [idiom.idiom for idiom in idioms]
            params['Язык/диалект'] = ', '.join(idioms_list)
        if poss:
            poss_list = [pos.pos for pos in poss]
            params['Часть речи'] = ', '.join(poss_list)
        if search_word:
            params['Слово/значение'] = search_word
        if morpheme:
            params['Морфема'] = morpheme
        if morph_type:
            params['Тип морфемы'] = morph_type
        if morph_gloss:
            params['Глосса'] = morph_gloss
        return params


class WordPageView(TemplateView):
    template_name = 'word_page.html'

    def get_context_data(self, **kwargs):
        context = super(WordPageView, self).get_context_data(**kwargs)
        word = Word.objects.filter(id=kwargs['word_id']).first()
        if word:
            context['word'] = word
            return context
        # else:


class SearchCognatesView(TemplateView):
    template_name = 'result_list.html'

    def get_context_data(self, **kwargs):
        context = super(SearchCognatesView, self).get_context_data(**kwargs)
        word = Word.objects.filter(id=kwargs['word_id']).first()
        root_id = MorphemeNumber.objects.filter(id=kwargs['root_id']).first()
        cognates = Word.objects.prefetch_related('morphemes').filter(
            morphemes__morph_type=MorphemeType.root(),
            morphemes__morph_number=root_id,
        ).exclude(idiom=word.idiom).order_by('-structure', 'entry_cyr')
        context['result_list'] = cognates
        context['search_params'] = self.get_used_search_params(word, root_id)
        return context

    def get_used_search_params(self, word, root_id):
        return {'Когнаты для корня': Morpheme.objects.filter(word=word, morph_number=root_id).first()}


class SearchSynonymsView(TemplateView):
    template_name = 'result_list.html'
    meaning_regex = r'(\(.+\))*(^|[,)]){}([ ,;]|$)'
    meaning_regex2 = r'(\(.+\))*(^|[ ,)]){}([,;]|$)'

    def get_context_data(self, **kwargs):
        context = super(SearchSynonymsView, self).get_context_data(**kwargs)
        word = Word.objects.filter(id=kwargs['word_id']).first()
        trans_ru = word.meaning_rus.split(', ')
        trans_eng = word.meaning_eng.split(', ')
        q = Q()
        for trans in trans_ru:
            q |= Q(meaning_rus__iregex=self.meaning_regex.format(trans))
            q |= Q(meaning_rus__iregex=self.meaning_regex2.format(trans))
        for trans in trans_eng:
            q |= Q(meaning_rus__iregex=self.meaning_regex.format(trans))
            q |= Q(meaning_rus__iregex=self.meaning_regex2.format(trans))
        synonyms = Word.objects.filter(q).exclude(id=word.id)
        context['result_list'] = synonyms
        context['search_params'] = self.get_used_search_params(word)
        return context

    def get_used_search_params(self, word):
        return {'Синонимы для слова': word}

class SearchMorphemesView(TemplateView):
    template_name = 'result_list.html'

    def get_context_data(self, **kwargs):
        context = super(SearchMorphemesView, self).get_context_data(**kwargs)
        word = Word.objects.filter(id=kwargs['word_id']).first()
        morpheme = Morpheme.objects.filter(id=kwargs['morpheme_id']).first().morpheme
        words = Word.objects.prefetch_related('morphemes').filter(morphemes__morpheme=morpheme).exclude(id=word.id)
        context['result_list'] = words
        context['search_params'] = self.get_used_search_params(morpheme)
        return context

    def get_used_search_params(self, morpheme):
        return {'Другие слова, содержащие': morpheme}
