from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pygame import mixer
import os
import json
import time
import threading

# ===== CONFIG =====
LOCAL_FOLDER = r"D:\MyFiles"       # Folder lokal
TOKEN_FILE = "token.json"          # File penyimpanan info file ter-upload
SOUND_DONE = "done.mp3"            # Sound effect kalau selesai upload

# ===== AUTHENTIKASI GOOGLE DRIVE =====
gauth = GoogleAuth()
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()
gauth.SaveCredentialsFile("mycreds.txt")

drive = GoogleDrive(gauth)

# ===== INISIALISASI SOUND SEKALI SAJA =====
mixer.init()

def play_sound():
    try:
        if os.path.exists(SOUND_DONE):
            mixer.music.load(SOUND_DONE)
            mixer.music.play()
            while mixer.music.get_busy():  # Tunggu sampai selesai
                time.sleep(0.1)
        else:
            print(f"[WARNING] File sound '{SOUND_DONE}' tidak ditemukan.")
    except Exception as e:
        print(f"[ERROR] Tidak bisa memutar sound: {e}")

def play_sound_async():
    threading.Thread(target=play_sound, daemon=True).start()

# ===== HELPERS =====
def load_uploaded_files():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                return {}
    return {}

def save_uploaded_files(uploaded_files):
    with open(TOKEN_FILE, "w") as f:
        json.dump(uploaded_files, f)

def create_drive_folder(name, parent_id=None):
    folder_metadata = {'title': name, 'mimeType': 'application/vnd.google-apps.folder'}
    if parent_id:
        folder_metadata['parents'] = [{'id': parent_id}]
    folder = drive.CreateFile(folder_metadata)
    folder.Upload()
    return folder['id']

def get_or_create_folder(folder_name, parent_id=None, folder_cache={}):
    key = f"{parent_id}_{folder_name}"
    if key in folder_cache:
        return folder_cache[key]

    query = f"title='{folder_name}' and mimeType='application/vnd.google-apps.folder'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    folder_list = drive.ListFile({'q': query}).GetList()
    if folder_list:
        folder_cache[key] = folder_list[0]['id']
        return folder_list[0]['id']

    folder_id = create_drive_folder(folder_name, parent_id)
    folder_cache[key] = folder_id
    return folder_id

def upload_file(filepath, parent_folder_id, uploaded_files):
    file_name = os.path.basename(filepath)
    last_modified = os.path.getmtime(filepath)

    # Cek kalau sudah pernah diupload dengan waktu modifikasi sama
    if filepath in uploaded_files and uploaded_files[filepath] == last_modified:
        print(f"[SKIP] {file_name} sudah ter-upload.")
        return False

    try:
        print(f"[UPLOAD] Mengunggah {file_name}...")
        file_drive = drive.CreateFile({'title': file_name, 'parents': [{'id': parent_folder_id}]})
        file_drive.SetContentFile(filepath)
        file_drive.Upload()

        # Simpan status hanya kalau upload sukses
        uploaded_files[filepath] = last_modified
        save_uploaded_files(uploaded_files)

        print(f"[DONE] {file_name} berhasil di-upload!")
        play_sound_async()  # Putar sound di thread terpisah
        return True
    except Exception as e:
        print(f"[ERROR] Gagal upload {file_name}: {e}")
        return False

def backup_folder(local_folder, parent_drive_id=None, folder_cache={}, uploaded_files={}):
    folder_name = os.path.basename(local_folder)
    drive_folder_id = get_or_create_folder(folder_name, parent_drive_id, folder_cache)

    uploaded_any = False
    for item in os.listdir(local_folder):
        path = os.path.join(local_folder, item)
        if os.path.isdir(path):
            if backup_folder(path, drive_folder_id, folder_cache, uploaded_files):
                uploaded_any = True
        else:
            if upload_file(path, drive_folder_id, uploaded_files):
                uploaded_any = True
    return uploaded_any

# ===== BACKUP LANGSUNG SAAT START =====
def start_backup():
    uploaded_files = load_uploaded_files()
    if backup_folder(LOCAL_FOLDER, uploaded_files=uploaded_files):
        save_uploaded_files(uploaded_files)
        print("[INFO] Semua file baru berhasil di-upload!")
    else:
        print("[INFO] Tidak ada file baru untuk di-upload.")

# ===== WATCHDOG EVENT HANDLER =====
class WatchHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print(f"[DETECT] File baru terdeteksi: {event.src_path}")
            uploaded_files = load_uploaded_files()
            folder_name = os.path.basename(LOCAL_FOLDER)
            drive_folder_id = get_or_create_folder(folder_name)
            upload_file(event.src_path, drive_folder_id, uploaded_files)

    def on_modified(self, event):
        if not event.is_directory:
            print(f"[DETECT] File diubah: {event.src_path}")
            uploaded_files = load_uploaded_files()
            folder_name = os.path.basename(LOCAL_FOLDER)
            drive_folder_id = get_or_create_folder(folder_name)
            upload_file(event.src_path, drive_folder_id, uploaded_files)

# ===== MAIN =====
if __name__ == "__main__":
    print("[INFO] Menjalankan backup awal...")
    start_backup()

    observer = Observer()
    observer.schedule(WatchHandler(), LOCAL_FOLDER, recursive=True)
    observer.start()

    print("=== Backup berjalan (real-time). Tekan Ctrl+C untuk berhenti. ===")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
