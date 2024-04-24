from datetime import datetime
from io import BytesIO
import pandas as pd
import zipfile

from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, FormView

from .forms import IdiomPosForm, SearchForm, ContactForm
from .models import Word, WordForm, Morpheme, MorphemeType


class StartPageView(FormView):
    template_name = 'index.html'
    form_class = ContactForm


class SearchView(FormView):
    template_name = 'search.html'
    form_class = SearchForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            search_word = form.cleaned_data.get('search_word')
            search_type = form.cleaned_data.get('search_type')
            idiom = form.cleaned_data.get('idiom')
            pos = form.cleaned_data.get('pos')

            q = Q(idiom__in=idiom) & Q(pos__in=pos)
            if search_type == '0':
                q &= Q(
                    Q(entry_cyr=search_word) | Q(entry_lat=search_word) |
                    Q(class_words_cyr__contains=search_word) | Q(class_words_lat__contains=search_word)
                )
            elif search_type == '1':
                q &= Q(Q(meaning_rus__icontains=search_word) | Q(meaning_eng__icontains=search_word))
            words = Word.objects.filter(q)
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
        morph_R = MorphemeType.objects.filter(morph_type='R').first()
        root_morph = word.morphemes.filter(morph_type=morph_R).first()
        root_number = root_morph.morph_number if root_morph else None
        if root_number:
            cognates = Word.objects.prefetch_related('morphemes').filter(
                morphemes__morph_type=morph_R,
                morphemes__morph_number=root_number,
            ).exclude(idiom=word.idiom).order_by('-structure', 'entry_cyr')
            context['result_list'] = cognates
        return context
