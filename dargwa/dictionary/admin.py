from django.conf.urls import url
from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

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
    Link,
    WordForm,
    Morpheme,
)


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    pass


class WordAdmin(admin.ModelAdmin):
    list_display = (
        'word',
        'transcription',
        'pos',
        'idiom',
        'gloss',
    )
    search_fields = (
        'word',
        'transcription',
        'gloss',
    )
    list_filter = (
        'pos',
        'idiom',
    )
    list_max_show_all = 1000
    change_list_template = 'admin/word/change_list.html'

    def update_links(self, request):
        words = Word.objects.filter(link_word_str__isnull=False)
        for word in words:
            link_word = Word.objects.filter(
                Q(word=word.link_word_str) | Q(transcription=word.link_word_str)). \
                filter(pos=word.pos, idiom=word.idiom).first()
            if link_word and not Link.objects.filter(word=word, link_word=link_word).exists():
                Link.objects.create(word=word, link_word=link_word)
        messages.success(request, 'Ссылки обновлены')
        return HttpResponseRedirect(reverse('admin:dictionary_word_changelist'))

    def get_urls(self):
        urls = super(WordAdmin, self).get_urls()
        my_urls = [
            url(
                r'^update_links/$',
                self.admin_site.admin_view(self.update_links),
                name='update_links',
            ),
        ]
        return my_urls + urls



admin.site.register(Word, WordAdmin)


@admin.register(Idiom)
class IdiomAdmin(admin.ModelAdmin):
    pass


@admin.register(PartOfSpeech)
class PartOfSpeechAdmin(admin.ModelAdmin):
    pass


@admin.register(GrammClass)
class GrammClassAdmin(admin.ModelAdmin):
    pass


@admin.register(Grammems)
class GrammemsAdmin(admin.ModelAdmin):
    pass


@admin.register(ArgumentStructure)
class ArgumentStructureAdmin(admin.ModelAdmin):
    pass


@admin.register(Root)
class RootAdmin(admin.ModelAdmin):
    pass


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    pass


@admin.register(Irregularity)
class IrregularityAdmin(admin.ModelAdmin):
    pass


@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    pass


@admin.register(Polysemy)
class PolysemyAdmin(admin.ModelAdmin):
    pass


@admin.register(Morpheme)
class MorphemeAdmin(admin.ModelAdmin):
    pass


@admin.register(WordForm)
class WordFormAdmin(admin.ModelAdmin):
    pass
