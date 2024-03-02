import os
import shutil
from collections import Counter, defaultdict
import math

import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords

FILES_PATH = "../task_2/html"
TOKENS_PATH = "tokens_tf_idf"
LEMMAS_PATH = "lemmas_tf_idf"
nltk.download("stopwords")


# извлекаем текст из HTML-файла
def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text


# токенизируем текст, приводим его к нижнему регистру и удаляем стоп-слова
def tokenize_and_clean(text):
    stop_words = set(stopwords.words('russian'))
    tokens = nltk.word_tokenize(text, language="russian")
    tokens = [token.lower() for token in tokens if token.isalpha() and token.lower() not in stop_words]
    return tokens


# лемматизация токенов
def lemmatize_tokens(tokens):
    morph = pymorphy2.MorphAnalyzer()
    lemmas = defaultdict(set)
    for token in tokens:
        p = morph.parse(token)[0]
        lemma = p.normal_form
        lemmas[lemma].add(token)
    return lemmas


# обрабатываем HTML-файлы, извлекаем токены и леммы из текста
def process_html_files(folder_path):
    all_tokens = set()
    all_lemmas = {}
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.html'):
            file_path = os.path.join(folder_path, file_name)
            text = extract_text_from_html(file_path)
            tokens = tokenize_and_clean(text)
            all_tokens.update(tokens)
            lemmas = lemmatize_tokens(tokens)
            for lemma, tokens_set in lemmas.items():
                if lemma not in all_lemmas:
                    all_lemmas[lemma] = set()
                all_lemmas[lemma].update(tokens_set)
    return all_tokens, all_lemmas


# вычисляем TF-IDF для токенов и лемм в каждом документе
def calculate_tf_idf(files_texts, all_tokens, all_lemmas):
    try:
        shutil.rmtree(TOKENS_PATH)
        shutil.rmtree(LEMMAS_PATH)
    except FileNotFoundError:
        pass

    os.makedirs(TOKENS_PATH, exist_ok=True)
    os.makedirs(LEMMAS_PATH, exist_ok=True)

    num_docs = len(files_texts)

    all_tokens_doc = ' '.join(all_tokens)
    all_tokens_counter = Counter(tokenize_and_clean(all_tokens_doc))

    for file_name, text in files_texts.items():
        text_cals = tokenize_and_clean(text)
        words_counter = Counter(text_cals)
        total_words = len(text_cals)

        # вычисляем TF-IDF для токенов
        for token in text_cals:
            tf = words_counter[token] / total_words
            df = all_tokens_counter[token]
            idf = math.log(num_docs / (df + 1))  # Добавляем 1 к df, чтобы избежать деления на ноль
            tf_idf = tf * idf
            new_filename = f"{file_name}.txt"
            with open(os.path.join(TOKENS_PATH, new_filename), "a", encoding="utf-8") as f:
                f.write(f"{token} {idf} {tf_idf}\n")

        # вычисляем TF-IDF для лемм
        for lemma, tokens_set in all_lemmas.items():
            tokens = [token for token in tokens_set if token in text_cals]
            if not tokens:
                continue  # пропускаем, если нет токенов для данной леммы
            tf_n = sum(words_counter[token] for token in tokens)
            total_lemma_words = total_words + tf_n
            df = sum(1 for text in files_texts.values() if any(token in text for token in tokens) or lemma in text)
            idf = math.log(num_docs / (df + 1))  # добавляем 1 к df, чтобы избежать деления на ноль
            tf = tf_n / total_lemma_words
            tf_idf = tf * idf
            new_filename = f"{file_name}.txt"
            with open(os.path.join(LEMMAS_PATH, new_filename), "a", encoding="utf-8") as f:
                f.write(f"{lemma} {idf} {tf_idf}\n")


if __name__ == "__main__":
    files_texts = {}
    for root, _, files in os.walk(FILES_PATH):
        for index, file in enumerate(sorted(files), 1):
            text = extract_text_from_html(os.path.join(root, file))
            files_texts[file] = text

    all_tokens, all_lemmas = process_html_files(FILES_PATH)

    calculate_tf_idf(files_texts, all_tokens, all_lemmas)
