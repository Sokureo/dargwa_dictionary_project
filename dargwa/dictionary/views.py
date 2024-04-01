import pandas as pd

from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
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
from .scripts import transcr, drg_cyr


class UploadDictionaryView(TemplateView):
    template_name = 'import_form.html'
    # form_class = DisposalFilterForm
    # success_url = reverse_lazy('bank_disposal_print')

    dia = {'ý': 'у',
           'ó': 'о',
           'á': 'а',
           'é': 'е',
           '́': '',
           'í': 'i',
           'ú': 'u'}

    def post(self, request):
        excel_file = request.FILES['excel_file']
        excel_reader = pd.ExcelFile(excel_file)
        for sheet in excel_reader.sheet_names:
            df = excel_reader.parse(sheet)
            df = df.fillna('')
            if sheet.lower() in ['verb', 'verbs', 'глагол', 'глаголы']:
                for indx, word in enumerate(df.get('word')):
                    transcription = self.get_field('transcription', df, indx)
                    class_words, class_words_trans = self.make_gender_words(
                        word,
                        transcription,
                    )
                    word_obj = Word.objects.create(
                        word=word,
                        link_word_str=self.get_field('link', df, indx),
                        transcription=transcription,
                        trans_ru=self.get_field('translation_ru', df, indx),
                        trans_eng=self.get_field('translation_eng', df, indx),
                        gloss=self.get_field('gloss', df, indx),
                        comment=self.get_field('comment', df, indx),
                        example=self.get_field('example', df, indx),
                        variant=self.get_field('variant', df, indx),
                        class_words=class_words,
                        class_words_trans=class_words_trans,
                        sound=self.get_field('sound', df, indx),
                        img=self.get_field('img', df, indx),
                        pos=self.get_pos(df, indx),
                        idiom=self.get_idiom(df, indx),
                        gramm_class=self.get_gramm_class(df, indx),
                        argument_structure=self.get_argument_structure(df, indx),
                        root_id=self.get_root_id(df, indx),
                        source=self.get_source(df, indx),
                        irregularity=self.get_irregularity(df, indx),
                        origin=self.get_origin(df, indx),
                        polysemy=self.get_polysemy(df, indx),
                    )
                    self.create_morphemes(df, indx, word_obj)
                    self.create_wordforms(df, indx, word_obj)

        return redirect('upload_dict')

    def create_morphemes(self, sheet, indx, word):
        morphs = [
            self.get_field('morph_1', sheet, indx),
            self.get_field('morph_2', sheet, indx),
            self.get_field('morph_3', sheet, indx),
            self.get_field('morph_4', sheet, indx),
            self.get_field('morph_5', sheet, indx),
        ]

        for indx, morph in enumerate(morphs):
            if morph:
                morpheme, type, number = morph.split(':')
                Morpheme.objects.create(
                    word=word,
                    morpheme=morpheme,
                    type=type,
                    number=number,
                    order_id=indx+1,
                )

    def create_wordforms(self, sheet, indx, word):
        wordforms = [
            'inf_ipfv',
            'inf_ipfv_trans',
            'aorist',
            'aorist_trans',
        ]
        for grammem in wordforms:
            wordform = self.get_field(grammem, sheet, indx)
            if wordform:
                grammem_obj, _ = Grammems.objects.get_or_create(
                    grammem=grammem,
                    pos=word.pos,
                )
                WordForm.objects.create(
                    word=word,
                    wordform=wordform,
                    grammem=grammem_obj,
                )

    def get_field(self, field_name, sheet, indx):
        field = sheet.get(field_name)
        return field[indx] if field is not None else None

    def get_pos(self, sheet, indx):
        pos = self.get_field('pos', sheet, indx)
        pos = 'verb'
        if pos:
            pos_obj, _ = PartOfSpeech.objects.get_or_create(pos=pos)
            return pos_obj
        return None

    def get_idiom(self, sheet, indx):
        idiom = self.get_field('idiom', sheet, indx)
        idiom = 'aqusha'
        if idiom:
            idiom_obj, _ = Idiom.objects.get_or_create(idiom=idiom)
            return idiom_obj
        return None

    def get_gramm_class(self, sheet, indx):
        gramm_class = self.get_field('synt_class', sheet, indx)
        if gramm_class:
            gramm_class_obj, _ = GrammClass.objects.get_or_create(gramm_class=gramm_class)
            return gramm_class_obj
        return None

    def get_argument_structure(self, sheet, indx):
        argument_structure = self.get_field('argument_structure', sheet, indx)
        if argument_structure:
            argument_structure_obj, _ = ArgumentStructure.objects.get_or_create(
                argument_structure=argument_structure,
            )
            return argument_structure_obj
        return None

    def get_root_id(self, sheet, indx):
        root_id = self.get_field('root_id', sheet, indx)
        if root_id:
            root_id_obj, _ = Root.objects.get_or_create(root_id=root_id)
            return root_id_obj
        return None

    def get_source(self, sheet, indx):
        source = self.get_field('source', sheet, indx)
        if source:
            source_obj, _ = Source.objects.get_or_create(source=source)
            return source_obj
        return None

    def get_irregularity(self, sheet, indx):
        irregularity = self.get_field('irregularities', sheet, indx)
        if irregularity:
            irregularity_obj, _ = Irregularity.objects.get_or_create(irregularity=irregularity)
            return irregularity_obj
        return None

    def get_origin(self, sheet, indx):
        origin = self.get_field('origin', sheet, indx)
        if origin:
            origin_obj, _ = Origin.objects.get_or_create(origin=origin)
            return origin_obj
        return None

    def get_polysemy(self, sheet, indx):
        polysemy = self.get_field('polysemy', sheet, indx)
        if polysemy:
            polysemy_obj, _ = Polysemy.objects.get_or_create(polysemy=polysemy)
            return polysemy_obj
        return None

    def make_gender_words(self, word, transcription):
        for letter in self.dia:
            if letter in transcription:
                transcription = transcription.replace(letter, self.dia[letter])
            if letter in word:
                word = word.replace(letter, self.dia[letter])

        tr_markers = ['b', 'w', 'r', 'd', '']
        markers = ['б', 'в', 'р', 'д', '']
        class_words_tr = list()

        for tr_marker in tr_markers:
            new_form = transcription.replace('CL', tr_marker).replace('-', '')
            class_words_tr.append(new_form)
        drg = list(drg_cyr.keys())
        cyr = list(drg_cyr.values())
        drg += ['CL', 'č’', 'k’', 'tː', 'sː', 'c’', 'ja', 'p’', 't’']
        cyr += ['к1']
        cyr_letters = list()
        word = word.replace('-', '')
        indx = 0
        while indx < len(word) - 1:
            letter = word[indx]
            next_letter = word[indx + 1]
            if letter + next_letter in cyr:
                indx += 1
                cyr_letters.append(letter + next_letter)
            elif letter not in ['1', '(', ')', ' ']:
                cyr_letters.append(letter)
            indx += 1
        if word[-1] not in cyr_letters[-1]:
            cyr_letters.append(word[-1])

        orth_words = [transcr(z.replace('-', '')) for z in class_words_tr]
        if word not in orth_words and word.replace('у1', 'ю') not in orth_words:
            drg_letters = list()
            transcription = transcription.replace('-', '')
            indx = 0
            if 'aʔi' in transcription:
                transcription = transcription.replace('aʔi', 'ai')
            while indx < len(transcription) - 1:
                letter = transcription[indx]
                next_letter = transcription[indx + 1]
                if letter + next_letter in drg:
                    indx += 1
                    drg_letters.append(letter + next_letter)
                elif letter not in [' ']:
                    drg_letters.append(letter)
                indx += 1
            if transcription[-1] not in drg_letters[-1]:
                drg_letters.append(transcription[-1])

            cl_index = [i for i, x in enumerate(drg_letters) if x == 'CL']
            class_words = list()
            try:
                cyr_markers = [cyr_letters[y] for y in cl_index]
                for mark in markers:
                    for cl in cl_index:
                        cyr_letters[cl] = mark
                    class_words.append(''.join(cyr_letters))
            except:
                cyr_markers = list()
            if cyr_markers != ['б'] and cyr_markers != ['д'] and cyr_markers != ['б', 'б'] \
                    and cyr_markers != ['п', 'п']:
                return None, class_words_tr
            else:
                return class_words, class_words_tr
        else:
            return orth_words, class_words_tr
