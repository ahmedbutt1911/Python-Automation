from os import scandir, rename, makedirs
from os.path import splitext, exists, join
from shutil import move
from time import sleep
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

source_dir = "C:/Users/ALee/Downloads"
dest_dir_video = "D:/Downloded videos"
dest_dir_image = "D:/Downloded images"
dest_dir_documents = "D:/Downloded documents"
dest_dir_sfx = "D:/SFX"
dest_dir_music = "D:/Music"

image_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
video_extensions = [".mp4", ".avi", ".mov", ".mkv"]
audio_extensions = [".m4a", ".flac", ".mp3", ".wav", ".wma", ".aac"]
document_extensions = [".doc", ".docx", ".pdf", ".xls", ".xlsx","pptx", ".txt", ".csv", ".zip", ".rar", ".7z"]

def create_directories():
    makedirs(dest_dir_video, exist_ok=True)
    makedirs(dest_dir_image, exist_ok=True)
    makedirs(dest_dir_documents, exist_ok=True)
    makedirs(dest_dir_sfx, exist_ok=True)
    makedirs(dest_dir_music, exist_ok=True)

create_directories()

def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1
    return name

def move_file(dest, entry, name):
    try:
        if not entry.is_file():
            return
        if not dest:
            logging.error(f"Destination path is empty for {name}")
            return
        if exists(f"{dest}/{name}"):
            unique_name = make_unique(dest, name)
            oldName = join(dest, name)
            newName = join(dest, unique_name)
            rename(oldName, newName)
        move(entry.path, dest)
        logging.info(f"Moved file: {name} to {dest}")
    except Exception as e:
        logging.error(f"Error moving file {name}: {e}")

class MoverHandler(FileSystemEventHandler):
    def on_modified(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                self.check_audio_files(entry, name)
                self.check_video_files(entry, name)
                self.check_image_files(entry, name)
                self.check_document_files(entry, name)

    def check_audio_files(self, entry, name):
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension):
                dest = dest_dir_music if entry.stat().st_size >= 10_000_000 else dest_dir_sfx
                move_file(dest, entry, name)

    def check_video_files(self, entry, name):
        for video_extension in video_extensions:
            if name.endswith(video_extension):
                move_file(dest_dir_video, entry, name)

    def check_image_files(self, entry, name):
        for image_extension in image_extensions:
            if name.endswith(image_extension):
                move_file(dest_dir_image, entry, name)

    def check_document_files(self, entry, name):
        for documents_extension in document_extensions:
            if name.endswith(documents_extension):
                move_file(dest_dir_documents, entry, name)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
