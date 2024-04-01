from django.contrib import admin

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


@admin.register(Word)
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
