from django.conf.urls import url
from django.contrib import admin, messages
from django.contrib.admin import AdminSite
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

from .views import (
    DeleteDictionaryView,
    ExportDictionaryView,
    ImportDictionaryView,
)
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


admin.site.site_header = 'Лексикографическая база даргинских идиомов'


class LinkAdmin(admin.ModelAdmin):
    pass


admin.site.register(Link, LinkAdmin)


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
            url(r'^import/$',
                self.admin_site.admin_view(ImportDictionaryView.as_view()),
                name='import_dict',
                ),
            url(r'^delete/$',
                self.admin_site.admin_view(DeleteDictionaryView.as_view()),
                name='delete_dict',
                ),
            url(r'^export/$',
                self.admin_site.admin_view(ExportDictionaryView.as_view()),
                name='export_dict',
                ),
        ]
        return my_urls + urls


admin.site.register(Word, WordAdmin)


class IdiomAdmin(admin.ModelAdmin):
    pass


admin.site.register(Idiom, IdiomAdmin)


class PartOfSpeechAdmin(admin.ModelAdmin):
    pass


admin.site.register(PartOfSpeech, PartOfSpeechAdmin)


class GrammClassAdmin(admin.ModelAdmin):
    pass


admin.site.register(GrammClass, GrammClassAdmin)


class GrammemsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Grammems, GrammemsAdmin)


class ArgumentStructureAdmin(admin.ModelAdmin):
    pass


admin.site.register(ArgumentStructure, ArgumentStructureAdmin)


class RootAdmin(admin.ModelAdmin):
    pass


admin.site.register(Root, RootAdmin)


class SourceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Source, SourceAdmin)


class IrregularityAdmin(admin.ModelAdmin):
    pass


admin.site.register(Irregularity, IrregularityAdmin)


class OriginAdmin(admin.ModelAdmin):
    pass


admin.site.register(Origin, OriginAdmin)


class PolysemyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Polysemy, PolysemyAdmin)


class MorphemeAdmin(admin.ModelAdmin):
    pass


admin.site.register(Morpheme, MorphemeAdmin)


class WordFormAdmin(admin.ModelAdmin):
    pass


admin.site.register(WordForm, WordFormAdmin)
