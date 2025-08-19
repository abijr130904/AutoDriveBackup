```
# Auto Drive Backup

Auto Drive Backup adalah script Python untuk **membackup folder lokal ke Google Drive secara otomatis**. Script ini:

- Mengupload semua file di folder lokal ke Google Drive.
- Memutar suara saat upload berhasil.
- Memantau folder secara real-time menggunakan Watchdog sehingga file baru atau yang diubah langsung ter-upload.
- Menyimpan status file yang sudah diupload agar tidak duplikat.

---

## Fitur

- Backup otomatis semua file dari folder lokal ke Google Drive.
- Real-time monitoring menggunakan Watchdog.
- Memutar suara (`done.mp3`) setiap kali upload berhasil.
- Menyimpan status file yang sudah diupload agar tidak di-upload ulang.

---

## Persiapan Proyek
### 1. Instalasi Python
Pastikan Python 3.10+ sudah terpasang dan `pip` tersedia.
### 2. Install Dependencies dengan perintah: pip install -r requirements.txt


## Setup Google Drive API
Kunjungi Google Cloud Console.
Buat project baru.
Aktifkan Google Drive API pada project tersebut.
Buat OAuth 2.0 Client ID dengan tipe aplikasi: Desktop App atau Web application.
Tambahkan Authorized redirect URIs:
http://localhost:8080/Callback
http://localhost:8080/
Download file credentials.json dan simpan di folder proyek.
Saat pertama dijalankan, script akan membuat mycreds.txt untuk menyimpan token akses.



## Konfigurasi Script
Buka file backup_drive.py, lalu sesuaikan:

LOCAL_FOLDER = r"D:\MyFiles"  # Folder repository lokal yang ingin dibackup
TOKEN_FILE = "token.json"      # File untuk menyimpan status file ter-upload
SOUND_DONE = "done.mp3"        # File sound yang diputar saat upload sukses


## Cara Menjalankan

Jalankan script ketik perintah : python backup_drive.py


Browser akan terbuka untuk login ke akun Google.
Setelah login, token akan tersimpan di mycreds.txt.
Script akan langsung mengupload semua file yang belum di-upload dan memutar suara saat selesai.
Script tetap berjalan untuk memantau folder secara real-time.
Tekan Ctrl+C untuk menghentikan script.
## Cara Kerja Script
Script membaca semua file di folder lokal.
Mengecek apakah file sudah pernah di-upload (dilihat dari token.json).
Jika belum, file akan diupload ke Google Drive.
File baru atau yang diubah akan langsung terdeteksi oleh Watchdog.
Setelah upload sukses, suara akan diputar.


## Struktur Folder Proyek
AutoDriveBackup/
│
├── backup_drive.py       # Script utama
├── done.mp3              # Sound effect upload berhasil
├── credentials.json      # Google API credentials
├── mycreds.txt           # Token Google Drive (auto-generate)
├── token.json            # Status file yang sudah di-upload
├── requirements.txt      # File dependencies
└── README.md             # Dokumentasi proyek





