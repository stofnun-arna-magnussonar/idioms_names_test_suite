import os, re
from tabulate import tabulate

city_translations = {
    'Copenhagen': ['Kaupmannahöfn'],
    'Aarhus': ['Árósar'],
    'Roskilde': ['Hróarskelda', 'Hróaskelda'],
    'Odense': ['Óðinsvé'],
    'Aalborg': ['Álaborg'],
    'Funen': ['Fjón'],
    'Zealand': ['Sjáland'],
    'Jutland': ['Jótland'],
    'Öresund': ['Eyrarsund'],
    'Elsinore': ['Helsingjaeyri'],
    'Stockholm': ['Stokkhólmur'],
    'Gothenburg': ['Gautaborg'],
    'Scania': ['Skánn'],
    'Trondheim': ['Þrándheimur'],
    'Ålesund': ['Álasund'],
    'Svalbard': ['Svalbarði'],
    'Finnmark': ['Finnmörk'],
    'Åland': ['Álandseyjar'],
    'Tórshavn': ['Þórshöfn'],
    'Edinburgh': ['Edinborg'],
    'Rome': ['Róm'],
    'Vienna': ['Vín'],
    'Munich': ['München'],
    'Nuremberg': ['Nurnberg', 'Nürnberg'],
    'Cologne': ['Köln'],
    'The Hague': ['Haag'],
    'Prague': ['Prag'],
    'Warsaw': ['Varsjá'],
    'Krakow': ['Kraká'],
    'Lisbon': ['Lissabon'],
    'Seville': ['Sevilla'],
    'Moscow': ['Moskva'],
    'St. Petersburg': ['Pétursborg'],
    'Belgrade': ['Belgrad'],
    'Athens': ['Aþena'],
    'Milan': ['Mílanó', 'Milano'],
    'Venice': ['Feneyjar'],
    'Florence': ['Flórens'],
    'Sicily': ['Sikiley'],
    'Naples': ['Napólí', 'Napoli'],
    'Turin': ['Tórínó', 'Torino'],
    'Tuscany': ['Toskana'],
    'Vatican City': ['Vatíkanið'],
    'Geneva': ['Genf'],
    'Versailles': ['Versalir'],
    'Bavaria': ['Bæjaraland'],
    'California': ['Kalifornía'],
    'Cape Town': ['Höfðaborg'],
    'Cairo': ['Kaíró'],
    'New Delhi': ['Nýja Delí'],
    'Easter Island': ['Páskaeyja'],
    'Paris': ['París'],
    'Berlin': ['Berlín']
}

city_translations_not_found_by_lemmatizer = ['München', 'Nurnberg', 'Nürnberg', 'Haag', 'Lissabon', 'Sevilla', 'Belgrad', 'Mílanó',
'Kaíró', 'Genf', 'Sikiley']

translation_path = "./translations_lemmatized/"
translation_dir = os.fsencode(translation_path)

line_dict = {}
sent_patterns = [(r"(.*?) is lovely this time of year", 'n'), 
                 (r"The flight from (.*?) to (.*?) was delayed until the morning", ('þ', 'e')), 
                 (r"She used to live in (.*?) but she always loved to visit (.*?[^\w]*[\w]*)", ('þ', 'o')), 
                 (r"Have you been to (.*?[^\w]*[\w]*)", 'e'), (r"(.*?) dreams of flying", 'o'), 
                 (r"(.*?) felt bad after the conversation", 'þ'), 
                 (r"(.*?) misses (.*?[^\w]*[\w]*)", ('n', 'e')), 
                 (r"(.*?) cares for (.*?[^\w]*[\w]*)", ('þ', 'o'))]

people_dict = {}
with open('people_names_gold.txt', 'r') as f:
    for line in f:
        text, names = line.strip().split('\t')
        people_dict[text] = {'names': names.split(',')}

def evaluate_name(source_name, case, lemmatized_translation, source_text):
    points = 0
    city_points = 0
    city_total = 0
    people_points = 0
    people_total = 0
    for i,name in enumerate(source_name):
        if name in city_translations:
            city_total += len(source_name)
            for city_translation in city_translations[name]:
                for lt in lemmatized_translation:
                    if lt[2].strip() == city_translation:
                        if len(lt[1]) > 1 and lt[1][3] == case[i]:
                            points += 1
                            city_points += 1
                        elif lt[0].strip() in city_translations_not_found_by_lemmatizer:
                            points += 1
                            city_points += 1
                        elif lt[0] == 'Sikileyjar' and case[i] == 'e':
                            points += 1
                            city_points += 1
        else:
            if source_text.strip() in people_dict and name in people_dict[source_text.strip()]['names']:
                people_total += len(source_name)
                for lt in lemmatized_translation:
                    if lt[2].strip() == name:
                        points += 1
                        people_points += 1
    return points, city_points, city_total, people_points, people_total
                    
total_items_pattern = 0

with open('source.txt', 'r') as f:
    for i, line in enumerate(f.readlines()):
        for sent_pattern in sent_patterns:
            match = re.search(sent_pattern[0], line)
            if match:
                line_dict[i] = (match.groups(), sent_pattern[1], line)    
                for match in match.groups():
                    total_items_pattern += 1


text_out = ''
system_scores = {}

for file in os.listdir(translation_dir):
    filename = os.fsdecode(file)
    with open(translation_path+filename, 'r') as f:
        total_score = 0
        total_items = 0
        total_city_points = 0
        total_city_total = 0
        total_people_points = 0
        total_people_total = 0
        line_list = []
        line_counter = 0
        for line in f:
            if line.startswith('___$TOKENIZED'):
                pass
            elif line.startswith('___$SENTENCE_BREAK'):
                line_score, city_points, city_total, people_points, people_total = evaluate_name(
                    line_dict[line_counter][0], line_dict[line_counter][1], line_list, line_dict[line_counter][2])
                total_items = city_total + people_total
                text_out += str(filename).lstrip('.').split('.')[0] + '\t' + ' '.join([entry[0] for entry in line_list])  + '\t' + str(line_dict[line_counter][0]) + '\t' + str(line_dict[line_counter][1])  + '\t' + str(line_score) + '\t' + '\n'
                total_score += line_score
                total_city_points += city_points
                total_city_total += city_total
                total_people_points += people_points
                total_people_total += people_total
                line_counter += 1
                line_list = []
                if line_counter == 912:
                    break
            else: 
                w, tag, lemma = line.strip().split('\t')
                line_list.append((w, tag, lemma))
    if total_score == 0:
        total_score += 1
    system_scores[filename] = {'Total Score': (total_city_points + total_people_points)/(total_city_total + total_people_total),
                              'Total Cities': total_city_total,
                              'Total City Score': total_city_points/total_city_total,
                              'Total People': total_people_total,
                              'Total People Score': total_people_points/total_people_total}
    print('System name:', filename)
    for key, value in system_scores[filename].items():
        print(key, value)
    print('\n')

table = []
for system in system_scores.keys():
    table.append([system, system_scores[system]['Total Score'], 
                  system_scores[system]['Total Cities'],
                  system_scores[system]['Total City Score'],
                  system_scores[system]['Total People'],
                  system_scores[system]['Total People Score']])
print(tabulate(table, headers=['System', 'Total Score',
                               'Total Cities', 'Total City Score',
                               'Total People', 'Total People Score']))


with open('model_scores.txt', 'w') as f:
    f.write(text_out)
