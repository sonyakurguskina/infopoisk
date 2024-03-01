import re
import pymorphy2
import json


# загрузка индекса из файла
def load_index(filename):
    index = {}
    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            data = json.loads(line)
            index[data["word"]] = set(data["inverted_array"])
    return index


# принимаем пользовательский запрос и индекс, вычисляем результаты поиска
def boolean_search(query, index):
    analyzer = pymorphy2.MorphAnalyzer()
    sets_stack = []
    ops_stack = []
    elements = re.findall(r'\(|\)|\w+|[^\s\w]', query)
    elements = list(filter(None, elements))  # разделение запроса на элементы

    for elem in elements:
        if elem in ["AND", "OR", "NOT", "(", ")"]:
            if elem == "(":
                ops_stack.append(elem)
            elif elem == ")":
                while ops_stack and ops_stack[-1] != "(":
                    execute_operator(ops_stack.pop(), sets_stack)
                ops_stack.pop()
            else:
                while ops_stack and operator_priority(elem) <= operator_priority(ops_stack[-1]):
                    execute_operator(ops_stack.pop(), sets_stack)
                ops_stack.append(elem)
        else:
            normalized_elem = analyzer.parse(elem)[0].normal_form
            if normalized_elem in index:
                sets_stack.append(index[normalized_elem])
            else:
                sets_stack.append({'0'})

    while ops_stack:
        execute_operator(ops_stack.pop(), sets_stack)

    return sorted(sets_stack[-1], key=int)


def execute_operator(op, stack):
    if op == "AND":
        b = stack.pop()
        a = stack.pop()
        stack.append(a & b)
    elif op == "OR":
        b = stack.pop()
        a = stack.pop()
        stack.append(a | b)
    elif op == "NOT":
        b = stack.pop()
        a = stack.pop()
        stack.append(a - b)


def operator_priority(op):
    priorities = {"NOT": 3, "AND": 2, "OR": 1}
    return priorities.get(op, 0)


filename = 'inverted_index.txt'
index = load_index(filename)

user_query = input("Введите ваш запрос: ")
search_results = boolean_search(user_query, index)

with open('../task_1/index.txt', 'r') as file:
    urls = file.read().splitlines()

# обработка пользовательского запроса
if search_results and not (len(search_results) == 1 and search_results[0] == '0'):
    with open('search_results.txt', 'w', encoding='utf-8') as output_file:
        output_file.write(f"Запрос: {user_query}\n")
        output_file.write("Результаты по запросу:\n")
        for res in search_results:
            if res != '0':
                output_file.write(urls[int(res) - 1] + "\n")
    print("Результаты записаны в файл 'search_results.txt'")
else:
    print("По запросу ничего не найдено")
