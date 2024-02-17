import requests
from bs4 import BeautifulSoup


def process_page(url, index_file):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            links = [link.get('href') for link in soup.find_all('a', href=True) if
                     link.get('href').startswith('https://')]
            filename = save_to_file(url, response.content)
            index_file.write(f"{url} : {filename}\n")
            return [link if link.startswith('/') else link for link in links[:30]]
    except Exception as e:
        print(f"Ошибка при обработке страницы {url}: {e}")
    return []


def save_to_file(url, content):
    filename = f"{url.replace('/', '_').replace(':', '')}.html"
    with open(filename, 'wb') as f:
        f.write(content)
    return filename


urls_to_process = ["https://klinikarassvet.ru/", "https://umedp.ru/", "https://medportal.ru/",
                   "https://www.krasotaimedicina.ru/", "https://docma.ru/", "https://fomin-clinic.ru/"]

with open("index.txt", "w") as index_file:
    while len(urls_to_process) > 0:
        url = urls_to_process.pop(0)
        new_links = process_page(url, index_file)
        urls_to_process.extend(new_links)

print("Процесс завершен.")
