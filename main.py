import os
import yt_dlp
import vk_api
from vk_api.upload import VkUpload
from vk_api.exceptions import VkApiError

# Параметры
YOUTUBE_CHANNEL_URLS = [
    'https://www.youtube.com/@MrBeast', 
]
VK_ACCESS_TOKEN = 'vk1.a.1diao11SW1H81p3BWC9neohed4Ba_pPaAGshPY3L5_zSptVT2tvjSZwSLBrGzPznomS7LB0-Pg8WDYLAl9A58iomUwQL31FmMz-uj4wrtu5vpc8A7zUIyv4ZmjmOOsOgKUJxsii8rzXTDaewDI009kQ0iRN3tYZBMTntruMA-EiepaiOSdMd-XY1ckKHmNkmR6RiZdw_s2yo0NAvlD3ZwQ'
GROUP_ID = '229137342'  # ID вашего сообщества в VK (без минуса)

MAX_DOWNLOADS = 1  # Максимальное количество видео для скачивания
DOWNLOAD_DIR = 'downloads'  # Папка для временных файлов


# Функция для скачивания видео с YouTube
def download_youtube_videos(channel_url, output_dir, max_downloads):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a][language=ru]/best',
        'noplaylist': True,
        'merge_output_format': 'mp4',
        'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
        'quiet': False
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([channel_url])


# Функция для создания плейлиста в VK
def create_playlist(vk_session, title, description, group_id):
    vk = vk_session.get_api()
    response = vk.video.addAlbum(
        group_id=group_id,
        title=title,
        description=description
    )
    playlist_id = response['album_id']
    print(f"Плейлист создан: {playlist_id}")
    return playlist_id


# Функция для загрузки видео в VK
def upload_to_vk(vk_session, file_path, group_id):
    vk_upload = VkUpload(vk_session)
    response = vk_upload.video(
        video_file=file_path,
        group_id=group_id,
        name=os.path.basename(file_path),
        description='Загружено автоматически'
    )
    print(f"Видео успешно загружено: {response['video_id']}")
    return response['video_id'], response['owner_id']


# Функция для добавления видео в плейлист
def add_video_to_playlist(vk_session, playlist_id, owner_id, video_id, group_id):
    vk = vk_session.get_api()
    response = vk.video.addToAlbum(
        target_id=f"-{group_id}",
        album_id=playlist_id,
        owner_id=owner_id,
        video_id=video_id
    )
    print(f"Видео {video_id} успешно добавлено в плейлист {playlist_id}. Ответ: {response}")


# Функция для удаления временных файлов
def clean_up(directory):
    print("Удаление временных файлов...")
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Удалён файл: {file_path}")

# Основной процесс
def main():
    try:
        # Инициализируем VK API сессию
        print("Подключение к VK API...")
        vk_session = vk_api.VkApi(token=VK_ACCESS_TOKEN)

        # Обрабатываем каждый канал из списка
        for channel_url in YOUTUBE_CHANNEL_URLS:
            print(f"Обработка канала: {channel_url}")
            
            # Получаем название канала из URL
            channel_name = channel_url.split('/')[-1]

            # Создаём папку для канала
            channel_download_dir = os.path.join(DOWNLOAD_DIR, channel_name)
            os.makedirs(channel_download_dir, exist_ok=True)

            # Скачиваем видео с канала
            print(f"Скачивание первых {MAX_DOWNLOADS} видео с канала {channel_name}...")
            download_youtube_videos(channel_url, channel_download_dir, MAX_DOWNLOADS)

            # Создаём плейлист в VK
            print(f"Создание плейлиста для канала {channel_name}...")
            playlist_id = create_playlist(
                vk_session,
                title=f"{channel_name}",
                description=f"Плейлист для канала {channel_name}",
                group_id=GROUP_ID
            )

            # Загружаем видео и добавляем в плейлист
            print(f"Загрузка видео в VK и добавление в плейлист {channel_name}...")
            for file_name in os.listdir(channel_download_dir):
                file_path = os.path.join(channel_download_dir, file_name)
                if os.path.isfile(file_path) and file_name.endswith(('.mp4', '.mkv', '.avi')):
                    print(f"Загрузка файла: {file_name}")
                    video_id, owner_id = upload_to_vk(vk_session, file_path, GROUP_ID)
                    add_video_to_playlist(vk_session, playlist_id, owner_id, video_id, GROUP_ID)

            # Удаляем временные файлы
            clean_up(channel_download_dir)

        print("Все каналы обработаны!")
    
    except Exception as e:
        print(f"Ошибка: {e}. Скрипт остановлен.")
        raise  # Повторно выбрасываем ошибку для отладки


if __name__ == "__main__":
    main()
