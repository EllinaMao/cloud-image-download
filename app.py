import os
import mimetypes
from datetime import datetime
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.core.exceptions import ResourceExistsError
from dotenv import load_dotenv


load_dotenv()

def upload_images_to_azure(container='my-container', directory='local_photos'):
    connection_string = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
    
    if not connection_string:
        print("Ошибка: Не найдена строка подключения AZURE_STORAGE_CONNECTION_STRING.")
        return

    container_name = container
    local_folder = directory

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)

    try:
        container_client.create_container()
        print(f"Создан новый контейнер: '{container_name}'")
    except ResourceExistsError:
        print(f"Контейнер '{container_name}' уже существует, продолжаем работу.")

    if not os.path.exists(local_folder):
        print(f"Ошибка: Папка '{local_folder}' не найдена в текущей директории.")
        return

    current_date = datetime.now().strftime('%Y-%m-%d')

    print("\nНачинается загрузка файлов...")

    for file_name in os.listdir(local_folder):
        file_path = os.path.join(local_folder, file_name)

        if os.path.isfile(file_path):
            blob_name = f"{current_date}/{file_name}"
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

            mime_type, _ = mimetypes.guess_type(file_path)
            content_type = mime_type if mime_type else "application/octet-stream"
            content_settings = ContentSettings(content_type=content_type)

            with open(file_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True, content_settings=content_settings)
            print(f"Загружен: {blob_name}")

    print("\nСписок всех файлов в контейнере:")
    print("-" * 60)
    blobs = container_client.list_blobs()
    
    for blob in blobs:
        size_kb = blob.size / 1024
        c_type = blob.content_settings.content_type
        print(f"Имя: {blob.name} | Тип: {c_type} | Размер: {size_kb:.2f} КБ")

if __name__ == "__main__":
    upload_images_to_azure()