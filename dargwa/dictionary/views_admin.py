from datetime import datetime
from io import BytesIO
import pandas as pd
import zipfile

from django.contrib import admin, messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView

from .forms import IdiomPosForm
from .serializers import NounSerializer, VerbSerializer
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
    WordForm,
    Morpheme,
)
from .scripts import make_gender_words


wordforms = {
    'verb': (
        'inf_ipfv',
        'inf_ipfv_trans',
        'aorist',
        'aorist_trans',
    ),
    'noun': (

    ),
}


class DeleteDictionaryView(FormView):
    template_name = 'admin/delete_dict.html'
    form_class = IdiomPosForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            idiom = form.cleaned_data.get('idiom')
            pos = form.cleaned_data.get('pos')
            query = Q(word__isnull=False)
            if idiom:
                query &= Q(idiom=idiom)
            if pos:
                query &= Q(pos=pos)
            words = Word.objects.filter(query)
            if words:
                words.delete()
                messages.success(request, 'Слова удалены')
            else:
                messages.error(request, 'Слова не найдены')
            return redirect('admin:dictionary_word_changelist')
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": Word._meta,
        }


class ExportDictionaryView(FormView):
    template_name = 'admin/export_dict.html'
    form_class = IdiomPosForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            idiom = form.cleaned_data.get('idiom')
            pos = form.cleaned_data.get('pos')
            query = Q(idiom__isnull=False)
            if idiom:
                query &= Q(idiom=idiom)
            idioms = Idiom.objects.filter(query)
            query = Q(pos__isnull=False)
            if pos:
                query &= Q(pos=pos)
            poss = PartOfSpeech.objects.filter(query)
            idiom_files = [self.write_idiom_excel(idiom, poss) for idiom in idioms]

            if len(idiom_files) > 1:
                archivename = f'lexicons_{datetime.now().strftime("%d.%m.%Y")}.zip'
                with BytesIO() as b:
                    with zipfile.ZipFile(b, 'w', zipfile.ZIP_DEFLATED) as zipObj:
                        for idiom_file in idiom_files:
                            zipObj.writestr(idiom_file['filename'], idiom_file['data'])
                    response = HttpResponse(
                        b.getvalue(),
                        content_type="application/zip",
                    )
                    response['Content-Disposition'] = f'attachment; filename={archivename}'
            else:
                response = HttpResponse(
                    idiom_files[0]['data'],
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )
                response['Content-Disposition'] = f'attachment; filename={idiom_files[0]["filename"]}'
            return response
        else:
            return self.form_invalid(form)

    def write_idiom_excel(self, idiom, poss):
        with BytesIO() as b:
            with pd.ExcelWriter(b) as writer:
                for pos in poss:
                    words_df = pd.DataFrame(self.get_lexicon_sheet(idiom, pos))
                    words_df.to_excel(
                        writer,
                        sheet_name=f'{idiom.idiom}_{pos.pos}',
                        index=False,
                    )
            filename = f'{idiom.idiom}_{datetime.now().strftime("%d.%m.%Y")}.xlsx'
            return {
                'data': b.getvalue(),
                'filename': filename,
            }

    def get_lexicon_sheet(self, idiom, pos):
        words = Word.objects.filter(idiom=idiom, pos=pos)
        if pos.pos == 'verb':
            data = VerbSerializer(words, many=True).data
        elif pos.pos == 'noun':
            data = NounSerializer(words, many=True).data
        else:
            data = [{}]
        return data

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": Word._meta,
        }


class ImportDictionaryView(TemplateView):
    template_name = 'admin/import_dict.html'

    def post(self, request):
        excel_file = request.FILES['excel_file']
        excel_reader = pd.ExcelFile(excel_file)
        for sheet in excel_reader.sheet_names:
            df = excel_reader.parse(sheet)
            df = df.fillna('')
            if sheet.lower() in ['verb', 'verbs', 'глагол', 'глаголы']:
                for indx, word in enumerate(df.get('word')):
                    transcription = self.get_field('transcription', df, indx)
                    class_words, class_words_trans = make_gender_words(
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

        messages.success(request, 'Словарь загружен')
        return redirect('admin:dictionary_word_changelist')

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

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **admin.site.each_context(self.request),
            "opts": Word._meta,
        }