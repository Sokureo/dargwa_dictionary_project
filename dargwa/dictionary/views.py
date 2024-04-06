from datetime import datetime
from io import BytesIO
import pandas as pd
import zipfile

from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView

from .forms import IdiomPosForm, SearchForm, ContactForm
from .serializers import NounSerializer, VerbSerializer
from .models import (
    Word,
    Idiom,
    PartOfSpeech,
    GrammClass,
    Grammems,
    ArgumentStructure,
    Root,
    Source,
    Irregularity,
    Origin,
    Polysemy,
    WordForm,
    Morpheme,
)
from .scripts import make_gender_words


wordforms = {
    'verb': (
        'inf_ipfv',
        'inf_ipfv_trans',
        'aorist',
        'aorist_trans',
    ),
    'noun': (

    ),
}


class StartPageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(StartPageView, self).get_context_data(**kwargs)
        context['search_form'] = SearchForm
        context['contact_form'] = ContactForm
        return context
