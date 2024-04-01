# -*- coding: utf-8 -*-
"""
Created on Mon Jun 11 01:45:33 2018

@author: oleg
"""

import re
import string


HEM = re.compile(r"(([iaeuptšsčcхkχ])ː)", re.I)  # Проверять через finditer
# ABR = re.compile(r'(([kpčtc])1)', re.I)
# PALKA = re.compile(r'(?<=[кпчцхгпт])[I1|l]', re.I)
# LAB = re.compile(r'(([кпчхгтпцъь:])в)', re.I)
# GLOT = re.compile(r'\bъ(?=[аоуеэи])',re.I)
#FAR_ABR = re.compile(r"(((?<=[^aouei]|\w)[iua])ˁ)|(([kpčtc])')", re.I)
FAR = re.compile(r'(((?<=[^aouei]|\w)[iua])[ˤˁ])', re.I)
ABR = re.compile(r"(([qkpčtc])[’'ʼ])", re.I)

J_VJ = re.compile(r'j[ua]', re.I)  # контексты, где ja -> я
E = re.compile(r'\be|e(?=[aouei])', re.I)  # контексты, где e -> э

# glot = 'ʔ'


drg_cyr = {'a': 'а',
            'á': 'а́',
           'aˤ': 'я',
           'aˁ': 'я',
           'áˁ': "я́",
           'b': 'б',
           'c': 'ц',
           'd': 'д',
           'e': 'е',
           'é':'е', # В начале слова и перед гласной это будет э
            'eˁ':'е1',   
           'f': 'ф',
           'g': 'г',
           'i': 'и',
           'í':'и́',
           'j': 'й',  # Йоты сделать
           'k': 'к',
           'l': 'л',
           'm': 'м',
           'n': 'н',
           'o': 'о',
           'p': 'п',
           'r': 'р',
           's': 'с',
           't': 'т',
           'u': 'у',
            'ú': 'у́',
           'w': 'в',
           'ʷ': 'в',
            '˳': 'в',
           'z': 'з',
           'č': 'ч',
           'š': 'ш',
           'ž': 'ж',
           'χ': 'х',
           'q': 'хъ',
           'q:': 'къ',
           'q’': 'кь',
           "q'": 'кь',
           'x': 'хь',
           'ʁ': 'гъ',
           'ʕ': 'гг',
           'ʡ': 'г1',
           'uˤ': 'ю',
           'ħ': 'х1',
           'h': 'гь',
           'ɢ': 'къ',
           'ʔ': 'ъ',
           'ʔe': 'э',
           'ˤ': '',
           'ˁ': '',
           'xː': 'хьхь',
           'qː': 'къ',
           'iˤ': 'и1',
           'eˤ': 'е1',
           'uˁ': 'у1',
           's:': 'сс',
           'k:': 'кк',
           'c:': 'цц',
           'q:': 'къ',
           'č:': 'чч',
           't:': 'тт',
           'š:': 'щ',
           'šː': 'щ'}


def transcr(drg_text):
    # print(drg_text)
    cyr = ''
    # try:
    J = {'ja': 'я',
         'ju': 'ю'}

    digr = ('ь', 'ъ')

    if 'iʔe' in drg_text:
        drg_text = drg_text.replace('iʔe', 'иэ')
    if 'aʔe' in drg_text:
        drg_text = drg_text.replace('aʔe', 'аэ')
    if 'uʔe' in drg_text:
        drg_text = drg_text.replace('uʔe', 'уэ')
    if drg_text.startswith('e') and not drg_text.startswith('eˁ'):
        drg_text = drg_text.replace('e', 'э', 1)
    if 'aˤː' in drg_text:
        drg_text = drg_text.replace('aˤː', 'яя')    


    drg_text = J_VJ.sub(lambda match: J[match.group()], drg_text)
    # drg_text = E.sub(r'э', drg_text)
    drg_text = FAR.sub(lambda match: drg_cyr.get(match.groups()[0],
                                                 match.group(2) + '1'), drg_text)
    drg_text = ABR.sub(lambda match: drg_cyr.get(match.groups()[0],
                                                 match.group(2) + '1'), drg_text)
    drg_text = HEM.sub(lambda match: drg_cyr[match.group(2)] * 2, drg_text)
    # print(drg_text)
    cyr = ''
    i = 0
    while i < len(drg_text) - 1:
        # extra_artic = False
        s = drg_text[i]
        if (not s.isalpha()) or (s in drg_cyr.values()) or (s in J.values()) or s in digr:
            cyr += drg_text[i]
        else:
            letter = drg_text[i]
            next_letter = drg_text[i + 1]
            if next_letter not in {"'", '’', 'ʼ', 'ː', 'ː', 'ː', 'ˤ', 'ˁ', ':'}:
                next_letter = ''
            else:
                # extra_artic = True
                i += 1
            # print(cyr)
            # if letter + next_letter == 'ː':
            #     cyr += cyr[-1]
            # else:
            cyr += drg_cyr[letter + next_letter]
        i += 1
    cyr += drg_cyr.get(drg_text[-1], drg_text[-1]) if drg_text[-1].isalnum() else ''
    # isalnum для случаев типа к1#'

    # except: pass
    # cyr = cyr.replace('1', 'I')
    return cyr

##########################################################################
HEM1 = re.compile(r'(([иаеупткшсчцх]|хь)\2)', re.I)  # Проверять через finditer
ABR1 = re.compile(r'(([кпчтпц])1)', re.I)
PALKA1 = re.compile(r'(?<=[кпчцхгпт])[I1|l]', re.I)
LAB1 = re.compile(r'(([кпчхгтпцъь:])в)', re.I)
# GLOT = re.compile(r'\bъ(?=[аоуеэи])',re.I)
FAR1 = re.compile(r'(?<=[ауэеи])1', re.I)  # Фарингализация незадних - бывает не во всех диалектах

J_VJ1 = re.compile(r'(?<=[аоуеиэюя])[яю]|\b([яю])', re.I)  # контексты, где я -> ja

# glot = 'ʔ'

regular = {HEM1: 'ː',
           ABR1: "’",
           FAR1: 'ˤ',
           LAB1: 'ʷ'}

cyr_drg = {'а': 'a',
            'аъ': 'aʔ',
            'á': 'á',
           'б': 'b',
           'в': 'w',
           'въ': 'wʔ',
           'г': 'g',
           'гъ': 'ʁ',
           'гь': 'h',
           'г1': 'ʡ',
           'гг': 'ʕ',
           'д': 'd',
           'е': 'e',
           'е1': 'eˁ',
           'ж': 'ž',
           'з': 'z',
           'зъ': 'zʔ',
           'и': 'i',
           'и1': 'iˤ',
           'иъ': 'iʔ',
            'и́': 'í',
           'й': 'j',
           'к': 'k',
           'къ': 'qː',
           'кь': 'q’',
           'л': 'l',
           'лъ': 'lʔ',
           'м': 'm',
           'мъ': 'mʔ',
           'н': 'n',
           'о': 'o',
           'п': 'p',
           'р': 'r',
           'ръ': 'rʔ',
           'с': 's',
           'т': 't',
           'у': 'u',
           'у1': 'uˤ',
           'уъ': 'uʔ',
            'у́': 'ú',
           'ф': 'f',
           'х': 'χ',
           'х1': 'ħ',
           'хъ': 'q',
           'хь': 'x',
           'ц': 'c',
           'ч': 'č',
           'ш': 'š',  # фаринг гласных - глсн + 1
           'щ': 'šː',
           'э': 'e',
           'ю': 'uˤ',  # Встречаются ли ю, ё, есть ли контексты с йотом??? ю редко будет в фарингализации
           'я': 'aˤ',
           "я́": 'áˁ',  # я - фарингализация. Какие гласные фаринг?
           'ъ': 'ʔ',
           'ё': 'uˁ',
           'ь': '',
           '1': ''}

J1 = {'я': 'ja',
     'ю': 'ju'}


def transcr_drg(cyr_text):
    # print(cyr_text)
    drg = ''
    flag = 0
    # try:
    if cyr_text != 'None':
        cyr_text = PALKA1.sub('1', cyr_text)
        cyr_text = J_VJ1.sub(lambda match: J1[match.group()], cyr_text)
        cyr_text = cyr_text.replace('гг', 'ʕ')  # Не получается хранить в словаре

        for pat in regular.keys():  # Замена в регулярных для фон знаков контекстах
            fon_znak = regular[pat]
            try:
                one = lambda match: match.group(2) + fon_znak
                cyr_text = pat.sub(one, cyr_text)
            except: flag = 1

        i = 0
        # is_digr = False
        while i < len(cyr_text) - 1:
            # is_digr = False
            s = cyr_text[i]
            if (not s.isalpha()) or (s in cyr_drg.values()) or (s in regular.values()):
                drg += cyr_text[i]
            else:
                letter = cyr_text[i].lower()
                next_letter = cyr_text[i + 1]
                if next_letter not in {'1', 'ъ', 'ь'}:
                    next_letter = ''
                else:
                    # is_digr = True
                    i += 1
                # try:
                # print(cyr_drg[letter + next_letter])
                drg += cyr_drg[letter + next_letter]
                # except: flag = 1

            i += 1

        drg += cyr_drg.get(cyr_text[-1], cyr_text[-1])
        # print(drg)
    # if flag == 1:
    #     print(cyr_text, drg)
    # except: pass
    # print(drg)
    return drg


cyrillic = re.compile("[а-яА-Я]+")


def imperative(aorist):
    imper_sg = imper_pl = None
    try:
        ending = re.findall(r"(.*)(-.*)", aorist)
        if re.match("-ib|-ub|-ur", ending[0][-1]) and transitivity == 'itr':
            imper_sg = ending[0][0] + "e"
            imper_pl = ending[0][0] + "a(ja)"
        elif re.match("-ib|-ub|-ur", ending[0][-1]) and transitivity == 'tr':
            imper_sg = ending[0][0] + "a(aˁ)"
            imper_pl = ending[0][0] + "a(ja)"
        elif re.match("-un", ending[0][-1]):
            imper_sg = ending[0][0] + "en"
            imper_pl = imper_sg + "ija"

    except:
        pass
    try:
      return ", ".join([string for string in (imper_sg, imper_pl)])
    except:
      return ""

def prohibitive(imperfect):
    prohib_sg = prohib_pl = None
    try:
        verbroot = "".join(re.findall(r"(.*)-un", imperfect))
        if transitivity == 'tr':
            prohib_sg = "ma" + verbroot + "it(it:a)"
            prohib_pl = "ma" + verbroot + "it:aja"
        elif transitivity == 'itr':
            prohib_sg = "ma" + verbroot + "ut(ut:a)"
            prohib_pl = "ma" + verbroot + "ut:aja"

    except:
        pass
    try:
      return ", ".join([string for string in (prohib_sg, prohib_pl)])
    except:
      return ""

def replace_class(verb):
    verb = verb.replace("꞊", "b")
    return verb.replace("-", "")


def palochka(word):
    word = word.replace('1', 'I')
    return word

