from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.db import models
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.urls import reverse

from .views_admin import (
    DeleteDictionaryView,
    ExportDictionaryView,
    ImportDictionaryView,
)
from .models import (
    Word,
    Idiom,
    PartOfSpeech,
    SyntacticClass,
    Gender,
    Grammems,
    CaseFrame,
    Structure,
    Source,
    Irregularities,
    Origin,
    Polysemy,
    Link,
    WordForm,
    Morpheme,
    MorphemeType,
    MorphemeNumber,
)
from .scripts import make_gender_words


admin.site.site_header = 'Лексикографическая база даргинских идиомов'


class LinkAdmin(admin.ModelAdmin):
    pass


admin.site.register(Link, LinkAdmin)


class WordInline(admin.TabularInline):
    extra = 1
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'rows': 1, 'cols': 60})},
    }


class MorphemeInline(WordInline):
    model = Morpheme


class WordFormsInline(WordInline):
    model = WordForm


class WordAdmin(admin.ModelAdmin):
    list_display = (
        'entry_cyr',
        'entry_lat',
        'pos',
        'idiom',
        'gloss',
    )
    search_fields = (
        'entry_lat',
        'entry_lat',
        'gloss',
    )
    list_filter = (
        'pos',
        'idiom',
    )
    inlines = (
        MorphemeInline,
        WordFormsInline,
    )
    list_max_show_all = 1000
    change_list_template = 'admin/word/change_list.html'

    def save_model(self, request, obj, form, change):
        obj.class_words_cyr, obj.class_words_lat = make_gender_words(
            obj.entry_cyr,
            obj.entry_lat,
        )
        super(WordAdmin, self).save_model(request, obj, form, change)

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


class SyntacticClassAdmin(admin.ModelAdmin):
    pass


admin.site.register(SyntacticClass, SyntacticClassAdmin)


class GenderAdmin(admin.ModelAdmin):
    pass


admin.site.register(Gender, GenderAdmin)


class GrammemsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Grammems, GrammemsAdmin)


class CaseFrameAdmin(admin.ModelAdmin):
    pass


admin.site.register(CaseFrame, CaseFrameAdmin)


class StructureAdmin(admin.ModelAdmin):
    pass


admin.site.register(Structure, StructureAdmin)


class SourceAdmin(admin.ModelAdmin):
    pass


admin.site.register(Source, SourceAdmin)


class IrregularitiesAdmin(admin.ModelAdmin):
    pass


admin.site.register(Irregularities, IrregularitiesAdmin)


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


class MorphemeTypeAdmin(admin.ModelAdmin):
    pass


admin.site.register(MorphemeType, MorphemeTypeAdmin)


class MorphemeNumberAdmin(admin.ModelAdmin):
    pass


admin.site.register(MorphemeNumber, MorphemeNumberAdmin)
