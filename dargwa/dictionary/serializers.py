from rest_framework import serializers

from .models import (
    Word,
    WordForm,
    Morpheme,
)


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = (
            'entry_cyr',
            'entry_lat',
            'link_cyr',
            'meaning_rus',
            'meaning_eng',
            'gloss',
            'polysemy',
            'structure',
            'morpheme_1',
            'morpheme_2',
            'morpheme_3',
            'morpheme_4',
            'morpheme_5',
            'origin',
            'word_class',
            'irregularities',
            'source',
            'sound',
            'comments',
        )
        # exclude = ('id', 'pos', 'idiom', 'class_words_cyr', 'class_words_lat', 'img',)

    structure = serializers.CharField()
    source = serializers.CharField()
    irregularities = serializers.CharField()
    origin = serializers.CharField()
    polysemy = serializers.CharField()
    comments = serializers.CharField()
    word_class = serializers.CharField(source='pos')
    morpheme_1 = serializers.SerializerMethodField()
    morpheme_2 = serializers.SerializerMethodField()
    morpheme_3 = serializers.SerializerMethodField()
    morpheme_4 = serializers.SerializerMethodField()
    morpheme_5 = serializers.SerializerMethodField()

    # def to_representation(self, instance):
    #
    #     # This map is used to transform the field names
    #     fields_map = {
    #         "CODE": "code",
    #         "PERSONNAME": "personName",
    #         "PERSONSURNAME": "personSurname",
    #     }
    #
    #     for key, value in fields_map.items():
    #         # Field name is changed. Ej: PERSONNAME => personName
    #         instance[value] = instance.pop(key)
    #
    #     return instance

    def make_morph(self, morph):
        if morph:
            morpheme = morph.morpheme
            morph_type = morph.morph_type.morph_type if morph.morph_type else ''
            morph_number = morph.morph_number.morph_number if morph.morph_number else ''
            return ':'.join([morpheme, morph_type, morph_number]).strip(':')
        return None

    def get_morpheme_1(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=1).first()
        if morph and morph.morph_number and obj.structure == 'NONDER':
            return morph.morph_number.morph_number
        return self.make_morph(morph)


    def get_morpheme_2(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=2).first()
        return self.make_morph(morph)

    def get_morpheme_3(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=3).first()
        return self.make_morph(morph)

    def get_morpheme_4(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=4).first()
        return self.make_morph(morph)

    def get_morpheme_5(self, obj):
        morph = Morpheme.objects.filter(word=obj, order_id=5).first()
        return self.make_morph(morph)


class VerbSerializer(WordSerializer):
    infinitive_ipfv_cyr = serializers.StringRelatedField(required=False)
    infinitive_ipfv_lat = serializers.StringRelatedField(required=False)
    pret_pfv_cyr = serializers.StringRelatedField(required=False)
    pret_ipfv_cyr = serializers.StringRelatedField(required=False)
    cvb_ipfv_cyr = serializers.StringRelatedField(required=False)
    cvb_ipfv_lat = serializers.StringRelatedField(required=False)
    pret_pfv_lat = serializers.StringRelatedField(required=False)
    pret_ipfv_lat = serializers.StringRelatedField(required=False)
    imp_pfv = serializers.StringRelatedField(required=False)
    imp_ipfv = serializers.StringRelatedField(required=False)
    stem_pfv = serializers.StringRelatedField(required=False)
    stem_ipfv = serializers.StringRelatedField(required=False)
    proh = serializers.StringRelatedField(required=False)
    case_frame = serializers.CharField()
    syntactic_class = serializers.CharField()

    class Meta:
        model = Word
        fields = (
            'entry_cyr',
            'entry_lat',
            'link_cyr',
            'infinitive_ipfv_cyr',
            'infinitive_ipfv_lat',
            'pret_pfv_cyr',
            'pret_ipfv_cyr',
            'pret_pfv_lat',
            'pret_ipfv_lat',
            'cvb_ipfv_cyr',
            'cvb_ipfv_lat',
            'imp_pfv',
            'imp_ipfv',
            'proh',
            'stem_pfv',
            'stem_ipfv',
            'meaning_rus',
            'meaning_eng',
            'gloss',
            'polysemy',
            'structure',
            'morpheme_1',
            'morpheme_2',
            'morpheme_3',
            'morpheme_4',
            'morpheme_5',
            'origin',
            'word_class',
            'syntactic_class',
            'case_frame',
            'irregularities',
            'source',
            'sound',
            'comments',
        )


class NounSerializer(WordSerializer):
    abs_pl_cyr = serializers.PrimaryKeyRelatedField(required=False)
    abs_pl_lat = serializers.StringRelatedField(required=False)
    erg_sg_lat = serializers.StringRelatedField(required=False)
    gen_sg_lat = serializers.StringRelatedField(required=False)
    dat_sg_lat = serializers.StringRelatedField(required=False)
    loc_sg_lat = serializers.StringRelatedField(required=False)
    gender = serializers.CharField()

    class Meta:
        model = Word
        fields = (
            'entry_cyr',
            'entry_lat',
            'link_cyr',
            'abs_pl_cyr',
            'abs_pl_lat',
            'erg_sg_lat',
            'gen_sg_lat',
            'dat_sg_lat',
            'loc_sg_lat',
            'meaning_rus',
            'meaning_eng',
            'gloss',
            'polysemy',
            'structure',
            'morpheme_1',
            'morpheme_2',
            'morpheme_3',
            'morpheme_4',
            'morpheme_5',
            'origin',
            'word_class',
            'gender',
            'irregularities',
            'source',
            'sound',
            'comments',
        )


class OtherSerializer(WordSerializer):
    case_frame = serializers.CharField()

    class Meta:
        model = Word
        fields = (
            'entry_cyr',
            'entry_lat',
            'link_cyr',
            'meaning_rus',
            'meaning_eng',
            'gloss',
            'polysemy',
            'structure',
            'morpheme_1',
            'morpheme_2',
            'morpheme_3',
            'morpheme_4',
            'morpheme_5',
            'origin',
            'word_class',
            'case_frame',
            'irregularities',
            'source',
            'sound',
            'comments',
        )
