from django.db import models


class Word(models.Model):
    entry_cyr = models.CharField(max_length=45, db_index=True)
    entry_lat = models.CharField(max_length=45, null=True, blank=True, db_index=True)
    link_cyr = models.CharField(max_length=45, null=True, blank=True, db_index=True)
    meaning_rus = models.CharField(max_length=250, null=True, blank=True, db_index=True)
    meaning_eng = models.CharField(max_length=250, null=True, blank=True, db_index=True)
    gloss = models.CharField(max_length=45, null=True, blank=True, db_index=True)
    polysemy = models.ForeignKey('Polysemy', on_delete=models.CASCADE, null=True, blank=True)
    structure = models.ForeignKey('Structure', on_delete=models.CASCADE, null=True, blank=True)
    origin = models.ForeignKey('Origin', on_delete=models.CASCADE, null=True, blank=True)
    pos = models.ForeignKey('PartOfSpeech', on_delete=models.CASCADE, related_name='word_class', null=True, blank=True)
    idiom = models.ForeignKey('Idiom', on_delete=models.CASCADE)
    syntactic_class = models.ForeignKey('SyntacticClass', on_delete=models.CASCADE, null=True, blank=True)
    gender = models.ForeignKey('Gender', on_delete=models.CASCADE, null=True, blank=True)
    irregularities = models.ForeignKey('Irregularities', on_delete=models.CASCADE, null=True, blank=True)
    case_frame = models.ForeignKey('CaseFrame', on_delete=models.CASCADE, null=True, blank=True)
    source = models.ForeignKey('Source', on_delete=models.CASCADE, null=True, blank=True)
    comments = models.CharField(max_length=2000, null=True, blank=True)
    sound = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    img = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    # список словоформ по родам на кириллице и латыни, сгенерированные автоматически
    class_words_cyr = models.CharField(max_length=256, null=True, blank=True, db_index=True)
    class_words_lat = models.CharField(max_length=256, null=True, blank=True, db_index=True)

    def __str__(self):
        return self.entry_cyr

    @property
    def omonyms(self):
        return Word.objects.filter(
            polysemy__isnull=False,
            polysemy=self.polysemy,
            pos=self.pos,
            idiom=self.idiom,
        ).distinct().values_list('meaning_rus', flat=True).order_by('meaning_rus')

    def syntactic_class_rus(self):
        values = {
            'tr': 'перех.',
            'itr': 'неперех.',
            'aff': 'аффект.',
            'tr/itr': 'перех./неперех.',
            'tr/aff': 'перех./аффект.',
            'impers': 'безличн.'
        }
        return values.get(self.syntactic_class.syntactic_class, None) if self.syntactic_class else None

    def pos_rus(self):
        values = {
            'adj': 'прил.',
            'adv': 'нареч.',
            'conj': 'союз',
            'cop': 'связка',
            'coverb': 'коверб',
            'question word': 'вопр. слово',
            'loc adv': 'локат. наречие',
            'n': 'сущ.',
            'n/adj': 'сущ./прил.',
            'idiom (np)': 'имен. сл.-соч.',
            'num': 'числ.',
            'numeral': 'числ.',
            'particle': 'част.',
            'postposition': 'послелог',
            'pronoun': 'мест.',
            'quantifier': 'квант.',
            'v': 'глаг.',
            'verb': 'глаг.',
            'idiom (vp)': 'глаг. сл.-соч.'
        }
        return values.get(self.pos.pos, None) if self.pos else None

    def roots(self):
        return self.morphemes.filter(morph_type=MorphemeType.root())

    def inf_ipfv_cyr(self):
        return WordForm.objects.filter(word=self, grammem__grammem='infinitive_ipfv_cyr').first()

    def inf_ipfv_lat(self):
        return WordForm.objects.filter(word=self, grammem__grammem='infinitive_ipfv_lat').first()

    def pret_pfv_cyr(self):
        return WordForm.objects.filter(word=self, grammem__grammem='pret_pfv_cyr').first()

    def pret_ipfv_cyr(self):
        return WordForm.objects.filter(word=self, grammem__grammem='pret_ipfv_cyr').first()

    def cvb_ipfv_cyr(self):
        return WordForm.objects.filter(word=self, grammem__grammem='cvb_ipfv_cyr').first()

    def cvb_ipfv_lat(self):
        return WordForm.objects.filter(word=self, grammem__grammem='cvb_ipfv_lat').first()

    def pret_pfv_lat(self):
        return WordForm.objects.filter(word=self, grammem__grammem='pret_pfv_lat').first()

    def pret_ipfv_lat(self):
        return WordForm.objects.filter(word=self, grammem__grammem='pret_ipfv_lat').first()

    def imp_pfv(self):
        return WordForm.objects.filter(word=self, grammem__grammem='imp_pfv').first()

    def imp_ipfv(self):
        return WordForm.objects.filter(word=self, grammem__grammem='imp_ipfv').first()

    def stem_pfv(self):
        return WordForm.objects.filter(word=self, grammem__grammem='stem_pfv').first()

    def stem_ipfv(self):
        return WordForm.objects.filter(word=self, grammem__grammem='stem_ipfv').first()

    def proh(self):
        return WordForm.objects.filter(word=self, grammem__grammem='proh').first()

    def abs_pl_cyr(self):
        return WordForm.objects.filter(word=self, grammem__grammem='abs_pl_cyr').first()

    def abs_pl_lat(self):
        return WordForm.objects.filter(word=self, grammem__grammem='abs_pl_lat').first()

    def erg_sg_lat(self):
        return WordForm.objects.filter(word=self, grammem__grammem='erg_sg_lat').first()

    def gen_sg_lat(self):
        return WordForm.objects.filter(word=self, grammem__grammem='gen_sg_lat').first()

    def dat_sg_lat(self):
        return WordForm.objects.filter(word=self, grammem__grammem='dat_sg_lat').first()

    def loc_sg_lat(self):
        return WordForm.objects.filter(word=self, grammem__grammem='loc_sg_lat').first()


class Link(models.Model):
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name='link_word')
    link_word = models.ForeignKey('Word', on_delete=models.CASCADE)

    def __str__(self):
        return self.word.entry_cyr + ' - ' + self.link_word.entry_cyr


class Idiom(models.Model):
    idiom = models.CharField(max_length=45, unique=True)
    rus = models.CharField(max_length=45, null=True, blank=True)

    def __str__(self):
        return self.idiom


class WordForm(models.Model):
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name='wordforms')
    wordform = models.CharField(max_length=45, db_index=True)
    grammem = models.ForeignKey('Grammems', on_delete=models.CASCADE)

    def __str__(self):
        return self.wordform


# граммемы типа abs_pl_cyr, infinitive_ipfv_lat
class Grammems(models.Model):
    grammem = models.CharField(max_length=20, unique=True)
    pos = models.ForeignKey('PartOfSpeech', on_delete=models.CASCADE)

    def __str__(self):
        return self.grammem.lower().replace('_', ' ')


# синтаксический класс глагола
class SyntacticClass(models.Model):
    syntactic_class = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.syntactic_class


# род существительных
class Gender(models.Model):
    gender = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.gender


class Morpheme(models.Model):
    morpheme = models.CharField(max_length=45, db_index=True)
    order_id = models.IntegerField(db_index=True)
    morph_type = models.ForeignKey('MorphemeType', on_delete=models.CASCADE, null=True, blank=True)
    morph_number = models.ForeignKey('MorphemeNumber', on_delete=models.CASCADE, null=True, blank=True)
    word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name='morphemes')

    def __str__(self):
        return self.morpheme


class MorphemeType(models.Model):
    morph_type = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.morph_type

    @classmethod
    def root(cls):
        return cls.objects.filter(morph_type='R').first()


class MorphemeNumber(models.Model):
    morph_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.morph_number

    @classmethod
    def gloss(cls):
        from django.db.models import Q
        return cls.objects.all().exclude(Q(morph_number__iregex=r'[0-9]')).order_by('morph_number')


# модель управления
class CaseFrame(models.Model):
    case_frame = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.case_frame


class Irregularities(models.Model):
    irregularity = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.irregularity


class Origin(models.Model):
    origin = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.origin


# омонимы, ROW132
class Polysemy(models.Model):
    polysemy = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.polysemy


class PartOfSpeech(models.Model):
    pos = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.pos


# NONDER - непроизводное слово, DER - производное слово
class Structure(models.Model):
    structure = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.structure


class Source(models.Model):
    source = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.source
