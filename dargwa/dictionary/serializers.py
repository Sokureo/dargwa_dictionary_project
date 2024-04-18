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
    infinitive_ipfv_cyr = serializers.SerializerMethodField()
    infinitive_ipfv_lat = serializers.SerializerMethodField()
    pret_pfv_cyr = serializers.SerializerMethodField()
    pret_ipfv_cyr = serializers.SerializerMethodField()
    cvb_ipfv_cyr = serializers.SerializerMethodField()
    cvb_ipfv_lat = serializers.SerializerMethodField()
    pret_pfv_lat = serializers.SerializerMethodField()
    pret_ipfv_lat = serializers.SerializerMethodField()
    imp_pfv = serializers.SerializerMethodField()
    imp_ipfv = serializers.SerializerMethodField()
    stem_pfv = serializers.SerializerMethodField()
    stem_ipfv = serializers.SerializerMethodField()
    proh = serializers.SerializerMethodField()
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

    def get_infinitive_ipfv_cyr(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='infinitive_ipfv_cyr').first()

    def get_infinitive_ipfv_lat(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='infinitive_ipfv_lat').first()

    def get_pret_pfv_cyr(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='pret_pfv_cyr').first()

    def get_pret_ipfv_cyr(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='pret_ipfv_cyr').first()

    def get_cvb_ipfv_cyr(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='cvb_ipfv_cyr').first()

    def get_cvb_ipfv_lat(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='cvb_ipfv_lat').first()

    def get_pret_pfv_lat(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='pret_pfv_lat').first()

    def get_pret_ipfv_lat(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='pret_ipfv_lat').first()

    def get_imp_pfv(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='imp_pfv').first()

    def get_imp_ipfv(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='imp_ipfv').first()

    def get_stem_pfv(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='stem_pfv').first()

    def get_stem_ipfv(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='stem_ipfv').first()

    def get_proh(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='proh').first()


class NounSerializer(WordSerializer):
    abs_pl_cyr = serializers.SerializerMethodField()
    abs_pl_lat = serializers.SerializerMethodField()
    erg_sg_lat = serializers.SerializerMethodField()
    gen_sg_lat = serializers.SerializerMethodField()
    dat_sg_lat = serializers.SerializerMethodField()
    loc_sg_lat = serializers.SerializerMethodField()
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

    def get_abs_pl_cyr(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='abs_pl_cyr').first()

    def get_abs_pl_lat(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='abs_pl_lat').first()

    def get_erg_sg_lat(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='erg_sg_lat').first()

    def get_gen_sg_lat(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='gen_sg_lat').first()

    def get_dat_sg_lat(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='dat_sg_lat').first()

    def get_loc_sg_lat(self, obj):
        return WordForm.objects.filter(word=obj, grammem__grammem='loc_sg_lat').first()


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
