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
from .models import Word


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
                print(1434)
                q &= Q(
                    Q(entry_cyr__contains=search_word) | Q(class_words_cyr__contains=search_word) |
                    Q(class_words_lat__contains=search_word) |
                    Q(meaning_rus__contains=search_word) | Q(meaning_eng__contains=search_word)
                )
            elif search_type == '1':
                q &= Q(gloss=search_word)
            elif search_type == '2':
                q &= Q(structure=search_word)
            print(q)
            words = Word.objects.filter(q)
            print(words)
            return render(request, 'result_list.html', {'result_list': words})
        else:
            return self.form_invalid(form)


class WordPageView(TemplateView):
    template_name = 'word_page.html'

    # def __init__(self, **kwargs):
    #     print(*kwargs)
    #     self.result_list = result_list
    #     super(SearchResultsView, self).__init__(**kwargs)
    #
    # def get(self, request, *args, **kwargs):
    #     print(request.sessiont.get('result_list'))
    #     context = self.get_context_data(**kwargs)
    #     return self.render_to_response(context)
    #
    # def get_context_data(self, **kwargs):
    #     print(*kwargs)
    #     context = super(SearchResultsView, self).get_context_data(**kwargs)
    #     # context['result_list'] = self.result_list
    #     return context
