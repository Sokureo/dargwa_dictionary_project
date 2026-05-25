from datetime import datetime
import pandas as pd
from io import BytesIO

from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import TemplateView, FormView
from django.urls import reverse_lazy
from django.utils.translation import gettext as _

from .forms import ContactForm, SearchForm, MorphSearchForm
from .models import Word, Morpheme, MorphemeType, MorphemeNumber, PartOfSpeech, Idiom, ContactMessage


class StartPageView(TemplateView):
    template_name = 'index.html'


class SearchView(FormView):
    template_name = 'search_word.html'
    form_class = SearchForm
    meaning_regex = r'(\(.+\))*(^|[,)]){}([ ,;]|$)'
    meaning_regex2 = r'(\(.+\))*(^|[ ,)]){}([,;]|$)'
    class_regex = "'{}'"

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = self.get_form()
            if form.is_valid():
                search_word = form.cleaned_data.get('search_word')
                search_meaning = form.cleaned_data.get('search_meaning')
                idiom = form.cleaned_data.get('idiom') or Idiom.objects.all()
                pos = form.cleaned_data.get('pos') or PartOfSpeech.objects.all()

                words = list()
                if search_word or search_meaning:
                    q = Q(idiom__in=idiom) & Q(pos__in=pos)
                    if search_word:
                        search_word = search_word.replace('|', '1').replace('I', '1')
                        q &= Q(
                            Q(entry_cyr=search_word) | Q(entry_lat=search_word) |
                            Q(class_words_cyr__iregex=self.class_regex.format(search_word)) |
                            Q(class_words_lat__iregex=self.class_regex.format(search_word))
                        )
                    if search_meaning:
                        q &= Q(
                            Q(meaning_rus__iregex=self.meaning_regex.format(search_meaning)) |
                            Q(meaning_rus__iregex=self.meaning_regex2.format(search_meaning)) |
                            Q(meaning_eng__iregex=self.meaning_regex.format(search_meaning)) |
                            Q(meaning_eng__iregex=self.meaning_regex2.format(search_meaning))
                        )
                    words = Word.objects.filter(q)

                if request.POST.get('export_format'):
                    return export_results(words, request.POST.get('export_format'))

                html = render_to_string('result_list_ajax.html', {
                    'result_list': words,
                }, request=request)

                return JsonResponse({'html': str(html)})
            else:
                return self.form_invalid(form)


class SearchMorphView(FormView):
    template_name = 'search_morph.html'
    form_class = MorphSearchForm

    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = self.get_form()
            if form.is_valid():
                morpheme = form.cleaned_data.get('morpheme')
                morph_type = form.cleaned_data.get('morph_type')
                morph_gloss = form.cleaned_data.get('morph_gloss')
                idiom = form.cleaned_data.get('idiom') or Idiom.objects.all()
                pos = form.cleaned_data.get('pos') or PartOfSpeech.objects.all()

                q = Q(idiom__in=idiom) & Q(pos__in=pos)
                words = list()
                if morph_type or morph_gloss or morpheme:
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

                if request.POST.get('export_format'):
                    return export_results(words, request.POST.get('export_format'))

                html = render_to_string('result_list_ajax.html', {
                    'result_list': words,
                }, request=request)

                return JsonResponse({'html': str(html)})
            else:
                return self.form_invalid(form)


class WordPageView(TemplateView):
    template_name = 'word_page.html'

    def get(self, request, *args, **kwargs):
        word = Word.objects.filter(id=kwargs['word_id']).first()
        if word:
            return super().get(request, *args, **kwargs)
        else:
            return render(request, 'error.html')

    def get_context_data(self, **kwargs):
        context = super(WordPageView, self).get_context_data(**kwargs)
        word = Word.objects.filter(id=kwargs['word_id']).first()
        if word:
            context['word'] = word
        return context


class SearchCognatesView(TemplateView):
    template_name = 'result_list.html'

    def get_cognates(self, word_id, root_id):
        word = Word.objects.filter(id=word_id).first()
        root_id = MorphemeNumber.objects.filter(id=root_id).first()
        cognates = Word.objects.prefetch_related('morphemes').filter(
            morphemes__morph_type=MorphemeType.root(),
            morphemes__morph_number=root_id,
        ).exclude(idiom=word.idiom).order_by('-structure', 'entry_cyr')
        return cognates

    def post(self, request, *args, **kwargs):
        cognates = self.get_cognates(kwargs['word_id'], kwargs['root_id'])
        export_format = request.POST.get('export_format')
        if export_format:
            return export_results(cognates, export_format)

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchCognatesView, self).get_context_data(**kwargs)
        context['result_list'] = self.get_cognates(kwargs['word_id'], kwargs['root_id'])
        context['search_params'] = self.get_used_search_params(kwargs['word_id'], kwargs['root_id'])
        return context

    def get_used_search_params(self, word_id, root_id):
        word = Word.objects.filter(id=word_id).first()
        return {_('Когнаты для корня'): Morpheme.objects.filter(word=word, morph_number=root_id).first()}


class SearchSynonymsView(TemplateView):
    template_name = 'result_list.html'
    meaning_regex = r'(\(.+\))*(^|[,)]){}([ ,;]|$)'
    meaning_regex2 = r'(\(.+\))*(^|[ ,)]){}([,;]|$)'

    def get_synonyms(self, word):
        trans_ru = word.meaning_rus.split(', ')
        trans_eng = word.meaning_eng.split(', ')
        q = Q()
        for trans in trans_ru:
            q |= Q(meaning_rus__iregex=self.meaning_regex.format(trans))
            q |= Q(meaning_rus__iregex=self.meaning_regex2.format(trans))
        for trans in trans_eng:
            q |= Q(meaning_rus__iregex=self.meaning_regex.format(trans))
            q |= Q(meaning_rus__iregex=self.meaning_regex2.format(trans))
        return Word.objects.filter(q).exclude(id=word.id)

    def post(self, request, *args, **kwargs):
        word = Word.objects.filter(id=kwargs['word_id']).first()
        synonyms = self.get_synonyms(word)
        export_format = request.POST.get('export_format')
        if export_format:
            return export_results(synonyms, export_format)

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchSynonymsView, self).get_context_data(**kwargs)
        word = Word.objects.filter(id=kwargs['word_id']).first()
        context['result_list'] = self.get_synonyms(word)
        context['search_params'] = self.get_used_search_params(word)
        return context

    def get_used_search_params(self, word):
        return {_('Синонимы для слова'): word}


class SearchMorphemesView(TemplateView):
    template_name = 'result_list.html'

    def get_morphemes(self, word_id, morpheme_id):
        word = Word.objects.filter(id=word_id).first()
        morpheme = Morpheme.objects.filter(id=morpheme_id).first().morpheme
        return Word.objects.prefetch_related('morphemes').filter(morphemes__morpheme=morpheme).exclude(id=word.id)

    def post(self, request, *args, **kwargs):
        morphemes = self.get_morphemes(kwargs['word_id'], kwargs['morpheme_id'])
        export_format = request.POST.get('export_format')
        if export_format:
            return export_results(morphemes, export_format)

        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(SearchMorphemesView, self).get_context_data(**kwargs)
        morpheme = Morpheme.objects.filter(id=kwargs['morpheme_id']).first().morpheme
        context['result_list'] = self.get_morphemes(kwargs['word_id'], kwargs['morpheme_id'])
        context['search_params'] = self.get_used_search_params(morpheme)
        return context

    def get_used_search_params(self, morpheme):
        return {_('Другие слова, содержащие'): morpheme}


class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('dictionary:contact')

    def form_valid(self, form):
        ContactMessage.objects.create(
            email=form.cleaned_data['email'],
            subject=form.cleaned_data['subject'],
            message=form.cleaned_data['message']
        )

        messages.success(self.request, _('Спасибо! Ваше сообщение отправлено.'))
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{form.fields[field].label}: {error}')

        return super().form_invalid(form)


def export_results(words, export_format='xlsx'):
    data = []
    for word in words:
        row = {
            'word_id': word.id,
            'word': word.entry_cyr or '',
            'transcription': word.entry_lat or '',
            'meaning_rus': word.meaning_rus or '',
            'meaning_eng': word.meaning_eng or '',
            'pos': word.pos.pos if word.pos else '',
            'idiom': word.idiom.idiom if word.idiom else '',
        }
        data.append(row)

    df = pd.DataFrame(data)

    if export_format == 'csv':
        csv_content = df.to_csv(index=False, sep='\t', encoding='utf-8-sig')
        response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="results_{datetime.now().strftime("%d.%m.%Y")}.csv"'
        return response
    else:
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Результаты поиска', index=False)

        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="results_{datetime.now().strftime("%d.%m.%Y")}.xlsx"'
        return response


def error_handler(request, exception=None):
    return render(request, 'error.html')
