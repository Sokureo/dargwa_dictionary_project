"""
URL configuration for dargwa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path

from .views import (
    StartPageView,
    SearchView,
    SearchMorphView,
    WordPageView,
    SearchCognatesView,
    SearchMorphemesView,
    SearchSynonymsView,
)

app_name = 'dictionary'

urlpatterns = [
    path('', StartPageView.as_view(), name='start_page'),
    path('search/', SearchView.as_view(), name='search'),
    path('morph_search/', SearchMorphView.as_view(), name='search_morph'),
    url(r'^word/(?P<word_id>\d+)/$', WordPageView.as_view(), name='word_page'),
    url(r'^search/cognates/(?P<word_id>\d+)/(?P<root_id>\d+)/$', SearchCognatesView.as_view(), name='search_cognates'),
    url(r'^search/synonyms/(?P<word_id>\d+)/$', SearchSynonymsView.as_view(), name='search_synonyms'),
    url(r'^search/morphemes/(?P<word_id>\d+)/(?P<morpheme_id>\d+)/$', SearchMorphemesView.as_view(), name='search_morphemes'),
]
