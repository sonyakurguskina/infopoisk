import json
import math
import os
from typing import Dict, List
from nltk import word_tokenize

LEMMAS_TFIDF = '../task_4/lemmas_tf_idf'
LEMMAS_TFIDF_PATH = '../task_4/lemmas_tf_idf/'
LEMMA_TOKENS_FILE = '../task_2/lemmatized_tokens_list.txt'
INVERTED_INDEX_FILE = 'inverted_index.json'


def get_inverted_index():
    with open(INVERTED_INDEX_FILE, encoding='utf-8') as file:
        json_index = file.readline()
        index = json.loads(json_index)
        return index


def load_lemma_tokens() -> Dict[str, str]:
    lemmas = {}
    with open(LEMMA_TOKENS_FILE, encoding='utf-8') as lemma_file:
        lines = lemma_file.readlines()
        for line in lines:
            line = line.rstrip('\n')
            words = line.split(' ')
            for word in words:
                lemmas[word] = words[0]
    return lemmas


def load_doc_to_lemma_tf_idf() -> Dict[str, Dict[str, float]]:
    result = {}
    for file_name in os.listdir(LEMMAS_TFIDF):
        with open(LEMMAS_TFIDF_PATH + file_name, encoding='utf-8') as tf_idf_file:
            lines = tf_idf_file.readlines()
            result[file_name] = {data[0]: float(data[2]) for data in [line.rstrip('\n').split(' ') for line in lines]}
    return result


def load_lemma_to_doc_tf_idf() -> Dict[str, Dict[str, float]]:
    result = {}
    for file_name in os.listdir(LEMMAS_TFIDF):
        with open(LEMMAS_TFIDF_PATH + file_name, encoding='utf-8') as tf_idf_file:
            lines = tf_idf_file.readlines()
            for line in lines:
                data = line.rstrip('\n').split(' ')
                lemma_to_docs_tf_idf = result.get(data[0], {})
                lemma_to_docs_tf_idf[file_name] = float(data[2])
                result[data[0]] = lemma_to_docs_tf_idf
    return result


def calculate_doc_vector_length(doc_to_words: Dict[str, float]):
    return math.sqrt(sum(i ** 2 for i in doc_to_words.values()))


def get_cosine_similarity(query_vector: List[str], doc_vector: Dict[str, float], doc_vector_len: int):
    return sum(doc_vector.get(token, 0) for token in query_vector) / len(query_vector) / doc_vector_len


def merge_or(set1, set2):
    return set1.union(set2)


docs_list = os.listdir(LEMMAS_TFIDF)
doc_to_lemma = load_doc_to_lemma_tf_idf()
lemma_to_doc = load_lemma_to_doc_tf_idf()
doc_lengths = {doc: calculate_doc_vector_length(doc_to_lemma[doc]) for doc in docs_list}
token_to_lemma = load_lemma_tokens()
inverted_index = get_inverted_index()


def search(user_input):
    tokens = word_tokenize(user_input, language='russian')
    lemmas = [token_to_lemma[token] for token in tokens if token in token_to_lemma]
    doc_set = set()

    for lemma in lemmas:
        doc_set = merge_or(doc_set, inverted_index.get(lemma, set()))
    results = {doc: get_cosine_similarity(lemmas, doc_to_lemma[str(doc) + '.txt'], doc_lengths[str(doc) + '.txt'])
               for doc in doc_set}
    return dict(sorted(results.items(), key=lambda r: r[1], reverse=True))


if __name__ == '__main__':
    while True:
        user_input = input("Input search expression:\n")
        if user_input.lower() == 'exit':
            exit()
        try:
            print(search(user_input))

        except Exception as e:
            print(f"Error occurred: {e}. Please try again")