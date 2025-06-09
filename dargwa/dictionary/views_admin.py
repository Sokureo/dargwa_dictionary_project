from datetime import datetime
from io import BytesIO
import pandas as pd
import zipfile

from django.contrib import admin, messages
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.generic import TemplateView, FormView

from .forms import IdiomPosForm
from .serializers import NounSerializer, VerbSerializer, OtherSerializer
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


wordforms = {
    'v': (
        'INFINITIVE_IPFV_CYR',
        'INFINITIVE_IPFV_LAT',
        'PRET_PFV_CYR',
        'PRET_IPFV_CYR',
        'CVB_IPFV_CYR',
        'CVB_IPFV_LAT',
        'PRET_PFV_LAT',
        'PRET_IPFV_LAT',
        'IMP_PFV',
        'IMP_IPFV',
        'PROH',
        'STEM_PFV',
        'STEM_IPFV',
    ),
    'n': (
        'ABS_PL_CYR',
        'ABS_PL_LAT',
        'ERG_SG_LAT',
        'GEN_SG_LAT',
        'DAT_SG_LAT',
        'LOC_SG_LAT',
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
            words = Word.objects.all()
            if idiom:
                words = Word.objects.filter(idiom=idiom)
            if pos:
                if pos == 'other':
                    words = words.exclude(pos__in=['v', 'n'])
                else:
                    words = words.filter(pos=pos)

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
            if idiom:
                idioms = Idiom.objects.filter(idiom=idiom)
            else:
                idioms = Idiom.objects.all()
            if pos:
                if pos == 'other':
                    poss = PartOfSpeech.objects.exclude(pos__in=['v', 'n'])
                else:
                    poss = PartOfSpeech.objects.filter(pos=pos)
            else:
                poss = PartOfSpeech.objects.all()

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
                    if pos.pos == 'n':
                        pos_name = 'nouns'
                    elif pos.pos == 'v':
                        pos_name = 'verbs'
                    else:
                        pos_name = 'other'
                    words_df.to_excel(
                        writer,
                        sheet_name=f'{idiom.idiom}_{pos_name}',
                        index=False,
                    )
            filename = f'{idiom.idiom}_{datetime.now().strftime("%d.%m.%Y")}.xlsx'
            return {
                'data': b.getvalue(),
                'filename': filename,
            }

    def get_lexicon_sheet(self, idiom, pos):
        words = Word.objects.filter(idiom=idiom, pos=pos)
        if pos.pos == 'v':
            data = VerbSerializer(words, many=True).data
        elif pos.pos == 'n':
            data = NounSerializer(words, many=True).data
        else:
            data = OtherSerializer(words, many=True).data
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
        with transaction.atomic():
            for sheet in excel_reader.sheet_names:
                df = excel_reader.parse(sheet)
                df = df.fillna('')
                if '_' in sheet:
                    idiom = sheet.split('_')[0]
                    for indx, word in enumerate(df.get('ENTRY_CYR')):
                        if word:
                            entry_lat = self.get_field('ENTRY_LAT', df, indx)
                            if entry_lat:
                                entry_lat = entry_lat.replace('с', 'c')
                            class_words_cyr, class_words_lat = make_gender_words(
                                word,
                                entry_lat,
                            )
                            word_obj = Word.objects.create(
                                entry_cyr=word,
                                link_cyr=self.get_field('LINK_CYR', df, indx),
                                entry_lat=entry_lat,
                                meaning_rus=self.get_field('MEANING_RUS', df, indx),
                                meaning_eng=self.get_field('MEANING_ENG', df, indx),
                                gloss=self.get_field('GLOSS', df, indx),
                                comments=self.get_field('COMMENTS', df, indx),
                                class_words_cyr=class_words_cyr,
                                class_words_lat=class_words_lat,
                                sound=self.get_field('SOUND', df, indx),
                                # img=self.get_field('img', df, indx),
                                pos=self.get_pos(df, indx),
                                idiom=self.get_idiom(idiom),
                                syntactic_class=self.get_syntactic_class(df, indx),
                                gender=self.get_gender(df, indx),
                                case_frame=self.get_case_frame(df, indx),
                                structure=self.get_structure(df, indx),
                                source=self.get_source(df, indx),
                                irregularities=self.get_irregularities(df, indx),
                                origin=self.get_origin(df, indx),
                                polysemy=self.get_polysemy(df, indx),
                            )
                            self.create_morphemes(df, indx, word_obj)
                            self.create_wordforms(df, indx, word_obj)

            messages.success(request, 'Словарь загружен')
        return redirect('admin:dictionary_word_changelist')

    def create_morphemes(self, sheet, indx, word):
        morphs = [
            self.get_field('MORPHEME_1', sheet, indx),
            self.get_field('MORPHEME_2', sheet, indx),
            self.get_field('MORPHEME_3', sheet, indx),
            self.get_field('MORPHEME_4', sheet, indx),
            self.get_field('MORPHEME_5', sheet, indx),
        ]

        for indx, morph in enumerate(morphs):
            if morph:
                morph = morph.strip(':')
                if ':' not in morph and morph.startswith('N'):
                    morpheme = word.entry_cyr
                    morph_type = 'R'
                    morph_number = morph
                else:
                    morph_data = morph.rsplit(':', 2)
                    if len(morph_data) == 2:
                        morpheme, morph_type, morph_number = [morph_data[0], morph_data[1], None]
                    elif len(morph_data) == 3:
                        morpheme, morph_type, morph_number = [morph_data[0], morph_data[1], morph_data[2]]
                    else:
                        morpheme = morph
                        morph_type = None
                        morph_number = None
                if morph_type:
                    morph_type_obj, _ = MorphemeType.objects.get_or_create(morph_type=morph_type)
                else:
                    morph_type_obj = None
                if morph_number:
                    if ' ' in morph_number:
                        morph_number = morph_number.split(' ')[0]
                    morph_number_obj, _ = MorphemeNumber.objects.get_or_create(morph_number=morph_number)
                else:
                    morph_number_obj = None
                Morpheme.objects.create(
                    word=word,
                    morpheme=morpheme,
                    morph_type=morph_type_obj,
                    morph_number=morph_number_obj,
                    order_id=indx+1,
                )

    def create_wordforms(self, sheet, indx, word):
        pos = word.pos
        if pos and pos.pos in ['n', 'v']:
            for grammem in wordforms[pos.pos]:
                wordform = self.get_field(grammem, sheet, indx)
                if wordform:
                    grammem_obj, _ = Grammems.objects.get_or_create(
                        grammem=grammem,
                        pos=pos,
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
        pos = self.get_field('WORD_CLASS', sheet, indx)
        if pos:
            pos_obj, _ = PartOfSpeech.objects.get_or_create(pos=pos)
            return pos_obj
        return None

    def get_idiom(self, idiom):
        idiom_obj, _ = Idiom.objects.get_or_create(idiom=idiom)
        return idiom_obj

    def get_syntactic_class(self, sheet, indx):
        syntactic_class = self.get_field('SYNTACTIC_CLASS', sheet, indx)
        if syntactic_class:
            syntactic_class_obj, _ = SyntacticClass.objects.get_or_create(syntactic_class=syntactic_class)
            return syntactic_class_obj
        return None

    def get_gender(self, sheet, indx):
        gender = self.get_field('GENDER', sheet, indx)
        if gender:
            gender_obj, _ = Gender.objects.get_or_create(gender=gender)
            return gender_obj
        return None

    def get_case_frame(self, sheet, indx):
        case_frame = self.get_field('CASE_FRAME', sheet, indx)
        if case_frame:
            case_frame_obj, _ = CaseFrame.objects.get_or_create(
                case_frame=case_frame,
            )
            return case_frame_obj
        return None

    def get_structure(self, sheet, indx):
        structure = self.get_field('STRUCTURE', sheet, indx)
        if structure:
            structure_obj, _ = Structure.objects.get_or_create(structure=structure)
            return structure_obj
        return None

    def get_source(self, sheet, indx):
        source = self.get_field('SOURCE', sheet, indx)
        if source:
            source_obj, _ = Source.objects.get_or_create(source=source)
            return source_obj
        return None

    def get_irregularities(self, sheet, indx):
        irregularities = self.get_field('IRREGULARITIES', sheet, indx)
        if irregularities:
            irregularities_obj, _ = Irregularities.objects.get_or_create(irregularity=irregularities)
            return irregularities_obj
        return None

    def get_origin(self, sheet, indx):
        origin = self.get_field('ORIGIN', sheet, indx)
        if origin:
            origin_obj, _ = Origin.objects.get_or_create(origin=origin)
            return origin_obj
        return None

    def get_polysemy(self, sheet, indx):
        polysemy = self.get_field('POLYSEMY', sheet, indx)
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
