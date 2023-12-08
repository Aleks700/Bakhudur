import zipfile
import os
import shutil
import io
import re

def extract_and_move_kml_from_folder(folder_path, output_folder):
    # Создаем новую папку "kmzUnzipper" внутри output_folder
    unzipper_folder = os.path.join(output_folder, "kmzUnzipper")
    os.makedirs(unzipper_folder, exist_ok=True)
    print("папка создана")

    # Проходимся по всем файлам в указанной папке и её подпапках
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".zip"):
                # Формируем путь к текущему zip-файлу
                zip_file_path = os.path.join(root, file)
                # Извлекаем .KML файлы из zip-файла
                extract_kml(zip_file_path, unzipper_folder)

    # После извлечения KML файлов, обрабатываем их вторым кодом
    process_kml_files(unzipper_folder)
    print("обработка KML файлов завершена")

def extract_kml(zip_file_path, output_folder):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        # Ищем все файлы типа .KMZ в корне архива
        kmz_files = [item.filename for item in zip_ref.infolist() if not item.is_dir() and item.filename.endswith(".KMZ")]

        for kmz_file in kmz_files:
            # Извлекаем .KML файлы из .KMZ
            with zip_ref.open(kmz_file) as kmz_src:
                kmz_content = kmz_src.read()
                with zipfile.ZipFile(io.BytesIO(kmz_content)) as kml_zip_ref:
                    for file_info in kml_zip_ref.infolist():
                        if file_info.is_dir():
                            continue
                        if file_info.filename.endswith(".KML"):
                            with kml_zip_ref.open(file_info) as kml_src, open(os.path.join(output_folder, os.path.basename(kmz_file) + "_" + os.path.basename(file_info.filename)), 'wb') as kml_dest:
                                shutil.copyfileobj(kml_src, kml_dest)
    print("конец итерации")

def remove_sources_to_last_folder(kml_content):
    # Ищем <Folder id="sources"> и последнее вхождение </Folder>
    pattern_sources = re.compile(r'<Folder id="sources">.*?</Folder>', re.DOTALL)
    pattern_last_folder = re.compile(r'</Folder>', re.DOTALL)

    sources_match = pattern_sources.search(kml_content)
    last_folder_match = pattern_last_folder.finditer(kml_content)

    if sources_match and last_folder_match:
        # Находим последнее вхождение </Folder>
        last_folder_position = list(last_folder_match)[-1].end()
        
        # Удаляем текст от <Folder id="sources"> до последнего </Folder> включительно
        kml_content = kml_content[:sources_match.start()] + kml_content[last_folder_position:]

        print("Текст удален от <Folder id=\"sources\"> до последнего </Folder> включительно")

    return kml_content

def remove_sources_to_last_folder_from_kml(kml_file_path):
    with open(kml_file_path, 'r', encoding='utf-8') as file:
        kml_content = file.read()

    # Удаление текста от <Folder id="sources"> до последнего </Folder> включительно
    kml_content = remove_sources_to_last_folder(kml_content)

    # Запись обновленного содержимого обратно в файл
    with open(kml_file_path, 'w', encoding='utf-8') as file:
        file.write(kml_content)

def process_kml_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".KML"):
                kml_file_path = os.path.join(root, file)
                remove_sources_to_last_folder_from_kml(kml_file_path)

# Остальной код остается без изменений

# Путь к файлам
zip_folder_path = r"C:\zip folder"  # путь к файлу зип
output_folder = r"C:\zip unpack"  # путь к файлу, куда распаковываем архив и перемещаем файлы kml

extract_and_move_kml_from_folder(zip_folder_path, output_folder)

