import os


def create_id_map(folder_path):
    # получаем список всех файлов в папке
    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

    # фильтруем список, оставляя только HTML-файлы
    html_files = [f for f in files if f.endswith('.html')]

    # Создаем словарь, сопоставляющий каждому файлу его ID
    file_to_id = {file_name: idx for idx, file_name in enumerate(html_files, start=1)}

    return file_to_id
