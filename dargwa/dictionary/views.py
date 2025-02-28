from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db.models import Q
from django.shortcuts import render
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from .forms import IdiomPosForm, SearchForm
from .models import Word, WordForm, Morpheme, MorphemeType, MorphemeNumber


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
    # meaning_regex = r'(?:\(.+?\))*?(?:^|[ ,)]){}(?:[ ,;]|$)'

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            search_word = form.cleaned_data.get('search_word')
            search_type = form.cleaned_data.get('search_type')
            idiom = form.cleaned_data.get('idiom')
            pos = form.cleaned_data.get('pos')
            morph_type = form.cleaned_data.get('morph_type')
            morph_gloss = form.cleaned_data.get('morph_gloss')
            morpheme = form.cleaned_data.get('morpheme')

            q = Q(idiom__in=idiom) & Q(pos__in=pos)
            words = list()
            if search_type == '0':
                if search_word:
                    q &= Q(
                        Q(entry_cyr=search_word) | Q(entry_lat=search_word) |
                        Q(class_words_cyr__contains=search_word) | Q(class_words_lat__contains=search_word)
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
            return render(request, 'result_list.html', {'result_list': words})
        else:
            return self.form_invalid(form)


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
        return context


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
        # synonyms = Word.objects.filter(
        #     Q(meaning_rus__iregex=self.meaning_regex.format(word.meaning_rus)) |
        #     Q(meaning_eng__iregex=self.meaning_regex.format(word.meaning_eng))
        # )
        synonyms = Word.objects.filter(q)
        context['result_list'] = synonyms
        return context


class SearchMorphemesView(TemplateView):
    template_name = 'result_list.html'

    def get_context_data(self, **kwargs):
        context = super(SearchMorphemesView, self).get_context_data(**kwargs)
        morpheme = Morpheme.objects.filter(id=kwargs['morpheme_id']).first().morpheme
        words = Word.objects.prefetch_related('morphemes').filter(morphemes__morpheme=morpheme)
        context['result_list'] = words
        return context
