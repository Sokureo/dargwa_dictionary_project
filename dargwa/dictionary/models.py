from django.db import models


class Word(models.Model):
    word = models.CharField(max_length=45)
    link_word_str = models.CharField(max_length=45)
    transcription = models.CharField(max_length=45, null=True, blank=True, db_index=True)
    trans_ru = models.CharField(max_length=45, null=True, blank=True, db_index=True)
    trans_eng = models.CharField(max_length=45, null=True, blank=True, db_index=True)
    gloss = models.CharField(max_length=45, null=True, blank=True, db_index=True)
    pos = models.ForeignKey('PartOfSpeech', on_delete=models.CASCADE)
    idiom = models.ForeignKey('Idiom', on_delete=models.CASCADE)
    gramm_class = models.ForeignKey('GrammClass', on_delete=models.CASCADE, null=True, blank=True)
    argument_structure = models.ForeignKey(
        'ArgumentStructure',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    root_id = models.ForeignKey('Root', on_delete=models.CASCADE, null=True, blank=True)
    source = models.ForeignKey('Source', on_delete=models.CASCADE, null=True, blank=True)
    comment = models.CharField(max_length=200, null=True, blank=True)
    example = models.CharField(max_length=200, null=True, blank=True)
    irregularity = models.ForeignKey('Irregularity', on_delete=models.CASCADE, null=True, blank=True)
    variant = models.CharField(max_length=50, null=True, blank=True)
    # список словоформ по родам + в транскрипции
    class_words = models.CharField(max_length=256, null=True, blank=True)
    class_words_trans = models.CharField(max_length=256, null=True, blank=True)
    origin = models.ForeignKey('Origin', on_delete=models.CASCADE, null=True, blank=True)
    polysemy = models.ForeignKey('Polysemy', on_delete=models.CASCADE, null=True, blank=True)
    sound = models.CharField(max_length=50, null=True, blank=True)
    img = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.word


class Link(models.Model):
    word = models.ForeignKey('Word', on_delete=models.CASCADE)
    link_word = models.ForeignKey('Word', on_delete=models.CASCADE, related_name='link_word')


class Idiom(models.Model):
    idiom = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.idiom


class WordForm(models.Model):
    word = models.ForeignKey('Word', on_delete=models.CASCADE)
    wordform = models.CharField(max_length=45, db_index=True)
    grammem = models.ForeignKey('Grammems', on_delete=models.CASCADE)

    def __str__(self):
        return self.wordform


# транзитивность или род
class GrammClass(models.Model):
    gramm_class = models.CharField(max_length=45, unique=True)

    def __str__(self):
        return self.gramm_class


class Morpheme(models.Model):
    morpheme = models.CharField(max_length=45, db_index=True)
    order_id = models.IntegerField()
    type = models.CharField(max_length=20)
    number = models.CharField(max_length=20, db_index=True)
    word = models.ForeignKey('Word', on_delete=models.CASCADE)

    def __str__(self):
        return self.morpheme


# граммемы типа aorist, stem_pfv
class Grammems(models.Model):
    grammem = models.CharField(max_length=20, unique=True)
    pos = models.ForeignKey('PartOfSpeech', on_delete=models.CASCADE)

    def __str__(self):
        return self.grammem


# модель управления
class ArgumentStructure(models.Model):
    argument_structure = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.argument_structure


class Irregularity(models.Model):
    irregularity = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.irregularity


class Origin(models.Model):
    origin = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.origin


class Polysemy(models.Model):
    polysemy = models.CharField(max_length=50, unique=True)


class PartOfSpeech(models.Model):
    pos = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.pos


# номер корня для поиска когнатов
class Root(models.Model):
    root_id = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.root_id


class Source(models.Model):
    source = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.source
