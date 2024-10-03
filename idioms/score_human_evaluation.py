import json
from tabulate import tabulate

from islenska import Bin

evalset_json = open('data/idioms.json')
evalset_idioms = json.load(evalset_json)
evalset_json.close()

translations_file = open('data/wmt24_translations.json')
idioms_translations = json.load(translations_file)
translations_file.close()

evaluations_file = open('human_evaluation/human_evaluation.tsv')
evaluations = evaluations_file.readlines()
evaluations_file.close()

s_names = ['AMI', 'Aya23', 'Claude-3.5', 'CommandR-plus', 'CycleL', 'Dubformer', 'GPT-4', 'IKUN-C', 'IKUN',
           'IOL_Research', 'Llama3-70B', 'ONLINE-A', 'ONLINE-B', 'ONLINE-G', 'TranssionMT', 'TSU-HITs', 'Unbabel-Tower70B']

sources_dict = {}

skip_file = open('data/skip.txt')
skip_sentences = skip_file.readlines()
skip_file.close()

skip_sentence_dict = {}
for sentence in skip_sentences:
    skip_sentence_dict[sentence.strip().replace("'",'').replace('"','').replace('\\','')] = True

# þarf að flækja listann, með positive cues og negative cues
def load_sources():
    for idiom in evalset_idioms:
        try:
            if idiom['idiomatic_ex_1'].replace('"', '').replace('\\', '').replace("'", '').replace('"', '').replace(
                    '\\', '') not in skip_sentence_dict:
                sources_dict[idiom['idiomatic_ex_1']] = {'idiom': idiom['idiom'], 'id': idiom['id'], 'type': 'idiomatic_ex_2'}
        except:
            pass
        try:
            if idiom['idiomatic_ex_2'].replace('"', '').replace('\\', '').replace("'", '').replace('"', '').replace(
                    '\\', '') not in skip_sentence_dict:
                sources_dict[idiom['idiomatic_ex_2']] = {'idiom': idiom['idiom'], 'id': idiom['id'], 'type': 'idiomatic_ex_2'}
        except:
            pass
        try:
            if idiom['literal_exam_1'].replace('"', '').replace('\\', '').replace("'", '').replace('"', '').replace(
                    '\\', '') not in skip_sentence_dict:
                sources_dict[idiom['literal_exam_1']] = {'idiom': idiom['idiom'], 'id': idiom['id'], 'type': 'literal_exam_1'}
        except:
            pass
        try:
            if idiom['literal_exam_2'].replace('"', '').replace('\\', '').replace("'", '').replace('"', '').replace(
                    '\\', '') not in skip_sentence_dict:
                sources_dict[idiom['literal_exam_2']] = {'idiom': idiom['idiom'], 'id': idiom['id'], 'type': 'literal_exam_2'}
        except:
            pass

translations_dict = {}
def load_translations():
    for idioms_translations_entry in idioms_translations:
        for translation_type in ('idiom_1', 'idiom_2', 'literal_1', 'literal_2'):
            for system_item in s_names:
                #if system_item == 'Unbabel-Tower70B':
                #    if translation_type == 'idiom_1':
                #        if idioms_translations_entry['id'] == 156:
                #            print(system_item, translation_type)
                #            print(idioms_translations_entry[system_item + '.en-is.txt_' + translation_type])
                try:
                    current = idioms_translations_entry[system_item + '.en-is.txt_' + translation_type].replace("  ", " ").replace("'", "").replace('\n', '').replace('„','').replace('“','').replace('"','')
                    if current in translations_dict:
                        translations_dict[current].append({'id': idioms_translations_entry['id'], 'type': translation_type, 'system': system_item})
                    else:
                        translations_dict[current] = [{'id': idioms_translations_entry['id'], 'type': translation_type, 'system': system_item}]
                except:
                    pass

load_sources()
load_translations()

system_results_dict = {}
for i in s_names:
    system_results_dict[i] = {'correct': 0, 'total': 0, 'correct_idioms': 0, 'total_idioms': 0, 'correct_literals': 0, 'total_literals': 0}

ctr = 0
for evaluation in evaluations:
    ctr += 1
    #print(ctr)
    evaluation = evaluation.strip().split('\t')
    results = evaluation[6]
    source_text = evaluation[7]
    translation_text = evaluation[8]
    # Bjarki:
    if translation_text not in skip_sentence_dict:
        current = translation_text.replace("  ", " ").replace('"','').replace("'", "").replace('\n', '').replace('„','').replace('“','')
    evaluation_systems = translations_dict[current]
    for evaluation_system in evaluation_systems:
        if source_text in sources_dict:
            system_results_dict[evaluation_system['system']]['total'] += 1
            if results.startswith('A'):
                system_results_dict[evaluation_system['system']]['correct'] += 1
            if sources_dict[source_text]['type'] in ('idiomatic_ex_1', 'idiomatic_ex_2'):
                system_results_dict[evaluation_system['system']]['total_idioms'] += 1
                if results.startswith('A'):
                    system_results_dict[evaluation_system['system']]['correct_idioms'] += 1
            elif sources_dict[source_text]['type'] in ('literal_exam_1', 'literal_exam_2'):
                system_results_dict[evaluation_system['system']]['total_literals'] += 1
                if results.startswith('A'):
                    system_results_dict[evaluation_system['system']]['correct_literals'] += 1

for system in s_names:
    if system_results_dict[system]['total'] > 0:
        print(system, 'Idiom Accuracy:', system_results_dict[system]['correct_idioms'] / system_results_dict[system]['total_idioms'], 'Literal Accuracy:', system_results_dict[system]['correct_literals'] / system_results_dict[system]['total_literals'], 'Total Accuracy:', system_results_dict[system]['correct'] / system_results_dict[system]['total'])
        print('Total:', system_results_dict[system]['total'])
        print('Correct:', system_results_dict[system]['correct'])
        print('Total idioms:', system_results_dict[system]['total_idioms'])
        print('Correct idioms:', system_results_dict[system]['correct_idioms'])
        print('Total literals:', system_results_dict[system]['total_literals'])
        print('Correct literals:', system_results_dict[system]['correct_literals'])
        print('\n')

table = []
for system in s_names:
    if system_results_dict[system]['total'] > 0:
        #print nicely formatted table with system name, correct idioms, total idioms, idiom accuracy, corract literals, total literals, literal accuracy, correct in total, total number and total accuracy
        table.append([system, system_results_dict[system]['correct_idioms'], system_results_dict[system]['total_idioms'], system_results_dict[system]['correct_idioms'] / system_results_dict[system]['total_idioms'], system_results_dict[system]['correct_literals'], system_results_dict[system]['total_literals'], system_results_dict[system]['correct_literals'] / system_results_dict[system]['total_literals'], system_results_dict[system]['correct'], system_results_dict[system]['total'], system_results_dict[system]['correct'] / system_results_dict[system]['total']])
print(tabulate(table, headers=['System', 'Correct Idioms', 'Total Idioms', 'Idiom Accuracy', 'Correct Literals', 'Total Literals', 'Literal Accuracy', 'Correct Total', 'Total', 'Total Accuracy']))
