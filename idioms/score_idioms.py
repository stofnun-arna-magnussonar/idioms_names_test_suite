import json
import sys

import tokenizer
from islenska import Bin

evalset_json = open('data/idioms.json')
evalset_idioms = json.load(evalset_json)
evalset_json.close()

translations_file = open('data/wmt24_translations.json')
idioms_translations = json.load(translations_file)
translations_file.close()


skip_file = open('data/skip.txt')
skip_sentences = skip_file.readlines()
skip_file.close()

skip_sentence_dict = {}
for sentence in skip_sentences:
    skip_sentence_dict[sentence.strip().replace("'",'').replace('"','').replace('\\','')] = True


evaluations_out_tsv = 'data/evaluations_out.tsv'

b = Bin()

s_names = ['AMI', 'Aya23', 'Claude-3.5', 'CommandR-plus', 'CycleL', 'Dubformer', 'GPT-4', 'IKUN-C', 'IKUN',
           'IOL_Research', 'Llama3-70B', 'ONLINE-A', 'ONLINE-B', 'ONLINE-G', 'TranssionMT', 'TSU-HITs', 'Unbabel-Tower70B']

# þarf að flækja listann, með positive cues og negative cues
def idiom_cues():
    idiomatic_cues = {}
    for idiom in evalset_idioms:
        try:
            idiomatic_cues[idiom['id']] = {'idiom': idiom['idiom'], 'idiomatic_ex_1': idiom['idiomatic_ex_1'], 'idiomatic_ex_2': idiom['idiomatic_ex_2'],
                                           'literal_ex_1': idiom['literal_exam_1'], 'literal_ex_2': idiom['literal_exam_2'],
                                           'idiomatic_1_positive': list(idiom['idiomatic_1_positive']), 'idiomatic_1_negative': list(idiom['idiomatic_1_negative']),
                                           'idiomatic_2_positive': list(idiom['idiomatic_2_positive']), 'idiomatic_2_negative': list(idiom['idiomatic_2_negative']),
                                           'literal_1_positive': list(idiom['literal_1_positive']), 'literal_1_negative': list(idiom['literal_1_negative']),
                                           'literal_2_positive': list(idiom['literal_2_positive']), 'literal_2_negative': list(idiom['literal_2_negative'])}
        except:
            print('Error:', idiom)
            sys.exit(1)
    return idiomatic_cues

def found_literal_cue(literal_cues: list[str], translation: str) -> bool:
    b = Bin()
    translation_tokens = list([token[1].lower() for token in tokenizer.tokenize(translation.replace('.','').replace('(','').replace(')','')) if token[0] == 6])
    if len(translation_tokens) > 0:
        for cue in literal_cues:
            try:
                # þarf að breyta og fletta upp með orðflokki
                # print(b.lookup(cue))
                try:
                    lemma_candidates = b.lookup(cue)
                    # hér að neðan þyrfti þá að taka [1] og allt undir því
                    b_id = lemma_candidates[1][0].bin_id
                    bm = b.lookup_id(b_id)
                    ordmyndir = set([b.bmynd for b in bm])
                except:
                    ordmyndir = set([cue])
                if translation.find('sleggju') > -1:
                    print('LC:', lemma_candidates)
                for ordmynd in ordmyndir:
                    if ordmynd in translation_tokens:
                        return True
            except:
                print('Error:', cue, translation, translation_tokens)
                sys.exit(1)
    return False

def get_wordforms(word: str, form: str) -> list[str]:
    b = Bin()
    bm = ''
    wordforms = []
    if form == 'l':
        lemma_candidates = b.lookup(word)
        # hér að neðan þyrfti þá að taka [1] og allt undir því
        bin_ids = list(set([lemma_candidates[1][i].bin_id for i in range(len(lemma_candidates[1]))]))
        wordforms = []
        for bin_id in bin_ids:
            bm = b.lookup_id(bin_id)
            wordforms.extend(list(set([b.bmynd for b in bm])))
            wordforms = list(set(wordforms))
    elif form == 'i':
        wordforms = list(set([word]))
    return wordforms

def check_tokens(tokenlist, forms_1, forms_2, mydistance):
    for i, token in enumerate(tokenlist):
        if token in forms_1:
            start = max(0, i - mydistance)
            end = min(len(tokenlist), i + mydistance + 1)
            for j in range(start, end):
                if tokenlist[j] in forms_2:
                    return True
    return False


def evaluate_idiom(translation: str, positive_cues: list[str], negative_cues: list[str]) -> (int, str):

    translation_tokens = list([token[1].lower() for token in tokenizer.tokenize(translation) if token[0] == 6])
    if len(translation_tokens) > 0:
        for cue in negative_cues:
            if isinstance(cue[0], list):
                word_1 = cue[0]
                wordforms_1 = get_wordforms(word_1[0], word_1[1])
                word_2 = cue[1]
                wordforms_2 = get_wordforms(word_2[0], word_2[1])
                distance = cue[2]
                if check_tokens(translation_tokens, wordforms_1, wordforms_2, distance):
                    return (0, "Rejected: '" + word_1[0] + "' and '" + word_2[0] + "' in translation.")
            else:
                word, form = cue[0], cue[1]
                wordforms = get_wordforms(word, form)

                for wf in wordforms:
                    if wf in translation_tokens:
                        return (0, "Rejected: '" + wf + "' in translation.")
        for cue in positive_cues:
            if isinstance(cue[0], list):
                word_1 = cue[0]
                wordforms_1 = get_wordforms(word_1[0], word_1[1])
                word_2 = cue[1]
                wordforms_2 = get_wordforms(word_2[0], word_2[1])
                distance = cue[2]
                if check_tokens(translation_tokens, wordforms_1, wordforms_2, distance):
                    return (1, "Accepted: '" + word_1[0] + "' and '" + word_2[0] + "' in translation.")
            else:
                word, form = cue[0], cue[1]
                wordforms = get_wordforms(word, form)

                for wf in wordforms:
                    if wf in translation_tokens:
                        return (1, "Accepted: '" + wf + "' in translation.")
    return (0, "Rejected: No cues found in translation.")

idiomatic_cues = idiom_cues()

with open(evaluations_out_tsv, 'w') as out_file:
    for s_name in s_names:
        correct_literal_translations = 0
        total_literal_translations = 0
        correct_idiomatic_translations = 0
        total_idiomatic_translations = 0
        idiomatic_1 = s_name + '.en-is.txt_idiom_1'
        idiomatic_2 = s_name + '.en-is.txt_idiom_2'
        literal_1 = s_name + '.en-is.txt_literal_1'
        literal_2 = s_name + '.en-is.txt_literal_2'

        for idiom_entry in idioms_translations:
            curr_id = idiom_entry['id']
            cues = idiomatic_cues[curr_id]
            #print(curr_id)
            #print(cues)
            if idiomatic_1 in idiom_entry and len(idiom_entry[idiomatic_1]) > 0:
                if idiomatic_cues[curr_id]['idiomatic_ex_1'].replace('"','').replace('\\','').replace("'",'').replace('"','').replace('\\','') not in skip_sentence_dict:
                    eval_value, eval_string = evaluate_idiom(idiom_entry[idiomatic_1], cues['idiomatic_1_positive'], cues['idiomatic_1_negative'])
                    correct_idiomatic_translations += eval_value
                    total_idiomatic_translations += 1
                    out_file.write(str(curr_id) + '\t' + idiomatic_1 + '\tidiomatic\t' + str(eval_value) + '\t' + str(cues['idiomatic_1_positive']).replace('\n', ' ') + '\t' + str(cues['idiomatic_1_negative']).replace('\n', ' ') + '\t' + cues['idiom'] + '\t'  + eval_string  + '\t' + cues['idiomatic_ex_1'] + '\t' + idiom_entry[idiomatic_1] + '\n')
            if idiomatic_2 in idiom_entry and len(idiom_entry[idiomatic_2]) > 0:
                if idiomatic_cues[curr_id]['idiomatic_ex_2'].replace('"','').replace('\\','').replace("'",'').replace('"','').replace('\\','') not in skip_sentence_dict:
                    eval_value, eval_string = evaluate_idiom(idiom_entry[idiomatic_2], cues['idiomatic_2_positive'], cues['idiomatic_2_negative'])
                    correct_idiomatic_translations += eval_value
                    total_idiomatic_translations += 1
                    out_file.write(str(curr_id) + '\t' + idiomatic_2 + '\tidiomatic\t' + str(eval_value) + '\t' + str(cues['idiomatic_2_positive']).replace('\n', ' ') + '\t' + str(cues['idiomatic_2_negative']).replace('\n', ' ') + '\t' + cues['idiom'] + '\t'  + eval_string  + '\t' + cues['idiomatic_ex_2'] + '\t' + idiom_entry[idiomatic_2] + '\n')
            if literal_1 in idiom_entry and len(idiom_entry[literal_1]) > 0:
                if idiomatic_cues[curr_id]['literal_ex_1'].replace('"','').replace('\\','').replace("'",'').replace('"','').replace('\\','') not in skip_sentence_dict:
                    eval_value, eval_string = evaluate_idiom(idiom_entry[literal_1], cues['literal_1_positive'], cues['literal_1_negative'])
                    correct_literal_translations += eval_value
                    total_literal_translations += 1
                    out_file.write(str(curr_id) + '\t' + literal_1 + '\tliteral\t' + str(eval_value) + '\t' + str(cues['literal_1_positive']).replace('\n', ' ') + '\t' + str(cues['literal_1_negative']).replace('\n', ' ') + '\t' + cues['idiom'] + '\t'  + eval_string  + '\t' + cues['literal_ex_1'] + '\t' + idiom_entry[literal_1] + '\n')
            if literal_2 in idiom_entry and len(idiom_entry[literal_2]) > 0:
                if idiomatic_cues[curr_id]['literal_ex_1'].replace('"','').replace('\\','').replace("'",'').replace('"','').replace('\\','') not in skip_sentence_dict:
                    eval_value, eval_string = evaluate_idiom(idiom_entry[literal_2], cues['literal_2_positive'], cues['literal_2_negative'])
                    correct_literal_translations += eval_value
                    total_literal_translations += 1
                    out_file.write(str(curr_id) + '\t' + literal_2 + '\tliteral\t' + str(eval_value) + '\t' + str(cues['literal_2_positive']).replace('\n', ' ') + '\t' + str(cues['literal_2_negative']).replace('\n', ' ') + '\t' + cues['idiom'] + '\t'  + eval_string  + '\t' + cues['literal_ex_2'] + '\t' + idiom_entry[literal_2] + '\n')

        total_score = correct_idiomatic_translations + correct_literal_translations
        if total_idiomatic_translations == 0:
            total_idiomatic_translations = 1
        if total_literal_translations == 0:
            total_literal_translations = 1

        print('System name:', s_name)
        print('Total score:', (correct_idiomatic_translations + correct_literal_translations) / (total_idiomatic_translations + total_literal_translations))
        print('Correct idiomatics:', str(correct_idiomatic_translations) + ' / '+ str(total_idiomatic_translations), 'Correct idiomatics:', str(correct_idiomatic_translations / total_idiomatic_translations))
        print('Correct literals:', str(correct_literal_translations) + ' / '+ str(total_literal_translations), 'Correct literals:', str(correct_literal_translations / total_literal_translations))
        print('\n')

