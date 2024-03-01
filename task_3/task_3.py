from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import pymorphy2
import os
import json

from to_dict import create_id_map

nltk.download('stopwords')
stop_words = set(stopwords.words('russian'))

morph = pymorphy2.MorphAnalyzer()


# извлечение текста из html
def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text


# разбивание текста на токены, приведение к нижнему регистру и удаление стоп-слов
def tokenize_and_clean(text):
    tokens = nltk.word_tokenize(text, language="russian")
    tokens = [token.lower() for token in tokens if token.isalpha() and token.lower() not in stop_words]
    return tokens

# лемматизация
def lemmatize_tokens(tokens, file_name):
    lemmas = {}
    for token in tokens:
        p = morph.parse(token)[0]
        lemma = p.normal_form
        if lemma not in lemmas:
            lemmas[lemma] = set()
        lemmas[lemma].add(file_name)  # Добавляем имя файла к лемме
    return lemmas

# создание инвертированного индекса
def process_html_files(folder_path):
    inverted_index = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.html'):
            file_path = os.path.join(folder_path, file_name)
            text = extract_text_from_html(file_path)
            tokens = tokenize_and_clean(text)
            lemmas = lemmatize_tokens(tokens, file_name)
            for lemma, files_set in lemmas.items():
                if lemma not in inverted_index:
                    inverted_index[lemma] = set()
                inverted_index[lemma].update(files_set)
    return inverted_index


folder_path = '../task_2/html'
inverted_index = process_html_files(folder_path)

dictionary = create_id_map(folder_path)
print('dictionary', dictionary)

# сохраняем инвертированный индекс в файл
with open("inverted_index.txt", "w", encoding="utf-8") as index_file:
    for lemma, files_set in inverted_index.items():
        # преобразуем имена файлов в их ID
        file_ids = [dictionary[file_name] for file_name in files_set]
        lemma_dict = {
            "word": lemma,
            "count": len(file_ids),
            "inverted_array": file_ids,  # сортируем для упорядоченности
            "names": ' '.join(files_set)
        }
        # преобразуем словарь в строку JSON и записываем в файл с переносом строки после каждого объекта
        index_file.write(json.dumps(lemma_dict, ensure_ascii=False) + '\n')
