# SIAKAD Flask + MySQL

Sistem Informasi Akademik (SIAKAD) sederhana berbasis Flask dan MySQL.

## Fitur
- Manajemen Siswa (CRUD)
- Manajemen Guru (CRUD)
- Manajemen Mata Pelajaran (CRUD)
- Manajemen Nilai
  - Input nilai (Tugas, UTS, UAS, Nilai Akhir otomatis)
  - Transkrip nilai siswa
  - Laporan/print nilai per kelas
- Sistem Login (Admin, Guru, Siswa)
- Dashboard statistik + grafik rata-rata nilai per mata pelajaran

## Struktur Folder
```
siakad/
├─ run.py
├─ requirements.txt
├─ .env.example
├─ schema.sql
├─ app/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ extensions.py
│  ├─ models.py
│  ├─ utils.py
│  ├─ blueprints/
│  │  ├─ auth/
│  │  │  └─ routes.py
│  │  ├─ main/
│  │  │  └─ routes.py
│  │  ├─ students/
│  │  │  └─ routes.py
│  │  ├─ teachers/
│  │  │  └─ routes.py
│  │  ├─ subjects/
│  │  │  └─ routes.py
│  │  └─ grades/
│  │     └─ routes.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ auth/login.html
│  │  ├─ dashboard.html
│  │  ├─ students/
│  │  │  ├─ index.html
│  │  │  ├─ create.html
│  │  │  ├─ edit.html
│  │  │  └─ detail.html
│  │  ├─ teachers/
│  │  │  ├─ index.html
│  │  │  ├─ create.html
│  │  │  └─ edit.html
│  │  ├─ subjects/
│  │  │  ├─ index.html
│  │  │  ├─ create.html
│  │  │  └─ edit.html
│  │  └─ grades/
│  │     ├─ select_input.html
│  │     ├─ input.html
│  │     ├─ transcript.html
│  │     ├─ report_select.html
│  │     └─ report_print.html
│  └─ static/
│     └─ css/styles.css
```

## Persiapan
1. Buat database MySQL, misal `siakad_db`.
2. Import skema tabel:
   ```sql
   SOURCE schema.sql;
   ```
3. Salin `.env.example` menjadi `.env` dan sesuaikan nilai variabel.
4. Buat virtualenv dan instal dependency:
   ```bash
   python -m venv .venv
   .venv/Scripts/activate
   pip install -r requirements.txt
   ```

## Menjalankan Aplikasi
```bash
python run.py
```
Buka http://127.0.0.1:5000

## Inisialisasi Admin Pertama
- Akses `http://127.0.0.1:5000/auth/init` untuk membuat akun Admin pertama kali.
- Setelah admin dibuat, rute ini akan dinonaktifkan.

## Catatan Pengguna & Role
- Admin: akses penuh (manage siswa, guru, mapel, input/lihat nilai, laporan).
- Guru: input/lihat nilai hanya untuk mapel yang diampu.
- Siswa: lihat transkrip nilai sendiri.

## Keamanan
- Password disimpan menggunakan hashing (Werkzeug/Flask-Login).
- Pembatasan akses berbasis role dengan decorator `role_required`.

## Cetak Laporan
- Gunakan halaman Laporan Kelas, pilih mata pelajaran dan kelas, lalu gunakan tombol Print (browser) pada tampilan khusus cetak.

## Troubleshooting
- Pastikan koneksi database di `.env` benar dan database sudah dibuat.
- Pada Windows, gunakan driver `PyMySQL` (sudah termasuk di requirements).
- Jika port 5000 sedang dipakai, jalankan Flask di port lain via env `FLASK_RUN_PORT` atau modifikasi `run.py`.
