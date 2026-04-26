from django import forms
from django.conf.urls import url
from django.contrib import admin, messages
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

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
    ContactMessage,
)
from .scripts import make_gender_words


admin.site.site_header = 'Лексикографическая база даргинских идиомов'


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    search_fields = (
        'word__link_cyr',
        'word__entry_cyr',
        'link_word__link_cyr',
        'link_word__entry_cyr',
    )


class WordInline(admin.TabularInline):
    extra = 1
    formfield_overrides = {
        models.CharField: {'widget': forms.TextInput(attrs={'rows': 1, 'cols': 60})},
    }


class MorphemeInline(WordInline):
    model = Morpheme


class WordFormsInline(WordInline):
    model = WordForm


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = (
        'entry_cyr',
        'entry_lat',
        'pos',
        'idiom',
        'meaning_rus',
        'meaning_eng',
        'gloss',
    )
    search_fields = (
        'entry_cyr',
        'entry_lat',
        'meaning_rus',
        'meaning_eng',
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
        words = Word.objects.filter(link_cyr__isnull=False)
        for word in words:
            link_word = Word.objects.filter(
                entry_cyr=word.link_cyr,
                idiom=word.idiom,
            ).exclude(id=word.id).first()
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


@admin.register(Idiom)
class IdiomAdmin(admin.ModelAdmin):
    pass


@admin.register(PartOfSpeech)
class PartOfSpeechAdmin(admin.ModelAdmin):
    pass


@admin.register(SyntacticClass)
class SyntacticClassAdmin(admin.ModelAdmin):
    pass


@admin.register(Gender)
class GenderAdmin(admin.ModelAdmin):
    pass


@admin.register(Grammems)
class GrammemsAdmin(admin.ModelAdmin):
    pass


@admin.register(CaseFrame)
class CaseFrameAdmin(admin.ModelAdmin):
    pass


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    pass


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    pass


@admin.register(Irregularities)
class IrregularitiesAdmin(admin.ModelAdmin):
    pass


@admin.register(Origin)
class OriginAdmin(admin.ModelAdmin):
    pass


@admin.register(Polysemy)
class PolysemyAdmin(admin.ModelAdmin):
    pass


@admin.register(Morpheme)
class MorphemeAdmin(admin.ModelAdmin):
    search_fields = (
        'morpheme',
        'morph_number__morph_number',
    )
    list_display = (
        'morpheme',
        'order_id',
        'morph_type',
        'morph_number',
        'word',
    )
    list_filter = (
        'morph_type',
        'order_id',
    )


@admin.register(WordForm)
class WordFormAdmin(admin.ModelAdmin):
    pass


@admin.register(MorphemeType)
class MorphemeTypeAdmin(admin.ModelAdmin):
    search_fields = (
        'morph_type',
    )


@admin.register(MorphemeNumber)
class MorphemeNumberAdmin(admin.ModelAdmin):
    search_fields = (
        'morph_number',
    )


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'email', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('email', 'subject', 'message')
    list_editable = ('is_read',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
        self.message_user(request, f'{queryset.count()} сообщений отмечено как прочитанные.')

    mark_as_read.short_description = _('Отметить как прочитанные')

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
        self.message_user(request, f'{queryset.count()} сообщений отмечено как непрочитанные.')

    mark_as_unread.short_description = _('Отметить как непрочитанные')
