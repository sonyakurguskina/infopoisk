from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
import pymorphy2
import os

# парсим текст из html файлов
def extract_text_from_html(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text(separator=' ', strip=True)
    return text


# скачиваем готовый набор стоп-слов для русского языка
nltk.download('stopwords')
stop_words = set(stopwords.words('russian'))


# токенизация и предварительная очистка от стоп-слов и мусора
def tokenize_and_clean(text):
    tokens = nltk.word_tokenize(text, language="russian")
    tokens = [token.lower() for token in tokens if token.isalpha() and token.lower() not in stop_words]
    return tokens


# инициализация объекта для лемматизации слов
morph = pymorphy2.MorphAnalyzer()

# лемматизация токенов
def lemmatize_tokens(tokens):
    lemmas = {}
    for token in tokens:
        # получение нормальной формы для каждого токена
        p = morph.parse(token)[0]
        lemma = p.normal_form
        if lemma not in lemmas:
            lemmas[lemma] = set()
        lemmas[lemma].add(token)
    return lemmas

# проходимся по каждой html странице и проводим токенизацию и лемматизацию
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


# перенесли в эту папку html страницы, которые спарсили раннее
folder_path = 'html'

all_tokens, all_lemmas = process_html_files(folder_path)

# сохранение списка токенов в файл
with open("tokens_list.txt", "w", encoding="utf-8") as tokens_file:
    for token in all_tokens:
        tokens_file.write(f"{token}\n")

# сохранение списка лемматизированных токенов в файл
with open("lemmatized_tokens_list.txt", "w", encoding="utf-8") as lemmas_file:
    for lemma, tokens_set in all_lemmas.items():
        lemmas_file.write(f"{lemma} {' '.join(tokens_set)}\n")
