from rest_framework import serializers

from .models import (
    Word,
    WordForm,
    Morpheme,
)


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        exclude = ('id', 'class_words', 'class_words_trans',)

    pos = serializers.CharField()
    idiom = serializers.CharField()
    gramm_class = serializers.CharField()
    argument_structure = serializers.CharField()
    root_id = serializers.CharField()
    source = serializers.CharField()
    irregularity = serializers.CharField()
    origin = serializers.CharField()
    polysemy = serializers.CharField()
    morph_1 = serializers.SerializerMethodField()
    morph_2 = serializers.SerializerMethodField()
    morph_3 = serializers.SerializerMethodField()
    morph_4 = serializers.SerializerMethodField()
    morph_5 = serializers.SerializerMethodField()

    def get_morph_1(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=1).first()
        if morph:
            return ':'.join([morph.morpheme, morph.type, morph.number]).strip(':')

    def get_morph_2(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=2).first()
        if morph:
            return ':'.join([morph.morpheme, morph.type, morph.number]).strip(':')

    def get_morph_3(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=3).first()
        if morph:
            return ':'.join([morph.morpheme, morph.type, morph.number]).strip(':')

    def get_morph_4(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=4).first()
        if morph:
            return ':'.join([morph.morpheme, morph.type, morph.number]).strip(':')

    def get_morph_5(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=5).first()
        if morph:
            return ':'.join([morph.morpheme, morph.type, morph.number]).strip(':')


class VerbSerializer(WordSerializer):
    aorist_trans = serializers.SerializerMethodField()

    def get_aorist_trans(self, obj):
        return WordForm.objects.filter(
            word=obj,
            grammem__grammem='aorist_trans',
            grammem__pos=obj.pos,
        ).first()


class NounSerializer(WordSerializer):
    erg = serializers.SerializerMethodField()

    def get_erg(self, obj):
        return WordForm.objects.filter(
            word=obj,
            grammem__grammem='erg',
            grammem__pos=obj.pos,
        ).first()
