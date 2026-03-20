# yts-dl

[![Language: English](https://img.shields.io/badge/Language-English-1f6feb?style=for-the-badge)](#english)
[![Bahasa Indonesia](https://img.shields.io/badge/Bahasa-Indonesia-0a7f5a?style=for-the-badge)](#bahasa-indonesia)

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Click](https://img.shields.io/badge/Click-CLI-2C2D72?logo=python&logoColor=white)](https://click.palletsprojects.com/)
[![Rich](https://img.shields.io/badge/Rich-Terminal_UI-FA5B3D)](https://github.com/Textualize/rich)
[![Requests](https://img.shields.io/badge/Requests-HTTP-20232A)](https://requests.readthedocs.io/)
[![TOML](https://img.shields.io/badge/TOML-Config-9C4121)](https://toml.io/en/)

Interactive terminal movie downloader powered by the YTS API. It supports local torrent clients, remote qBittorrent, and clipboard export with a clean Rich-based UI.

---

## English

### Overview

yts-dl is a Python CLI app for searching and selecting movies from YTS, then sending the magnet link to your preferred destination:

- Local torrent client (macOS/Linux/Windows)
- Remote qBittorrent (homelab/server)
- Clipboard (copy magnet link)

### Features

- Interactive main menu with guided prompts
- Movie discovery commands:
	- `search` by title
	- `top` by rating
	- `trending` by latest additions
- Torrent quality picker (720p, 1080p, 1080p.x265, 2160p, 3D)
- Global behavior overrides: `--local`, `--remote`, `--quality`
- Remote setup wizard with qBittorrent connection test
- Error handling for API/network failures with retry prompts

### Requirements

- Python 3.10+
- Dependencies:
	- `click`
	- `rich`
	- `requests`
	- `tomllib` (builtin on Python 3.11+) or `tomli` fallback

### Installation

Run directly without installation:

```bash
python main.py
```

Or install in editable mode:

```bash
python -m pip install -e .
```

Then use:

```bash
yts-dl
```

If your shell cannot find the command, run it from your virtual environment:

```bash
.venv/bin/yts-dl
```

### Configuration

Config file location:

```text
~/.config/yts-dl/config.toml
```

Example:

```toml
[local]
default_mode = "local" # "local" or "remote"

[remote]
host = "http://192.168.1.x:8080"
username = "admin"
password = ""
save_path = "/mnt/storage/movies"
```

Setup wizard:

```bash
yts-dl config setup
```

Show current configuration:

```bash
yts-dl config show
```

### Usage

Main interactive menu:

```bash
yts-dl
```

Commands:

```bash
yts-dl search [QUERY]
yts-dl top [--genre GENRE] [--min-rating FLOAT] [--quality QUALITY]
yts-dl trending [--quality QUALITY]
yts-dl config setup
yts-dl config show
```

Global flags:

```bash
--remote    # force remote qBittorrent destination
--local     # force local torrent client destination
--quality   # 720p | 1080p | 1080p.x265 | 2160p | 3D
```

Examples:

```bash
yts-dl search inception --quality 1080p --remote
yts-dl top --genre action --min-rating 7.5
yts-dl trending --local
```

### Project Structure

```text
yts-dl/
├── main.py              # CLI entrypoint and interactive flows
├── api.py               # YTS API integration
├── qbit.py              # qBittorrent Web API client
├── config.py            # Config load/save and setup wizard
├── ui.py                # Rich UI helpers (tables, panels, spinner)
├── utils.py             # Magnet builder, local open, clipboard helpers
├── requirements.txt
└── pyproject.toml
```

### Operational Notes

- If `--remote` is used and config does not exist yet, setup wizard is prompted.
- If remote qBittorrent is unreachable, the app can offer a local fallback.
- If clipboard tools are unavailable, magnet link is printed as fallback.
- Press `Ctrl+C` anytime to exit safely.

### Troubleshooting

- `command not found: yts-dl`
	- Activate your environment or run `.venv/bin/yts-dl`.
- qBittorrent connection failure
	- Verify host URL, credentials, port, and network access.
- No search results
	- Try broader keywords or remove quality constraints.

### Disclaimer

Use this software responsibly and in compliance with applicable laws in your region. You are solely responsible for the content you access or download.

---

## Bahasa Indonesia

### Ringkasan

yts-dl adalah aplikasi CLI Python untuk mencari film dari YTS lalu mengirim magnet link ke tujuan yang diinginkan:

- Torrent client lokal (macOS/Linux/Windows)
- qBittorrent remote (homelab/server)
- Clipboard (salin magnet link)

### Fitur

- Menu interaktif utama dengan prompt terarah
- Perintah pencarian film:
	- `search` berdasarkan judul
	- `top` berdasarkan rating
	- `trending` berdasarkan film terbaru
- Pemilih kualitas torrent (720p, 1080p, 1080p.x265, 2160p, 3D)
- Override perilaku global: `--local`, `--remote`, `--quality`
- Setup wizard remote dengan tes koneksi qBittorrent
- Penanganan error API/jaringan dengan opsi retry

### Persyaratan

- Python 3.10+
- Dependensi:
	- `click`
	- `rich`
	- `requests`
	- `tomllib` (builtin Python 3.11+) atau fallback `tomli`

### Instalasi

Jalankan langsung tanpa instalasi package:

```bash
python main.py
```

Atau install editable (disarankan untuk development):

```bash
python -m pip install -e .
```

Lalu jalankan:

```bash
yts-dl
```

Jika command tidak ditemukan oleh shell, jalankan dari virtualenv:

```bash
.venv/bin/yts-dl
```

### Konfigurasi

Lokasi file konfigurasi:

```text
~/.config/yts-dl/config.toml
```

Contoh:

```toml
[local]
default_mode = "local" # "local" atau "remote"

[remote]
host = "http://192.168.1.x:8080"
username = "admin"
password = ""
save_path = "/mnt/storage/movies"
```

Setup wizard:

```bash
yts-dl config setup
```

Tampilkan konfigurasi aktif:

```bash
yts-dl config show
```

### Penggunaan

Menu interaktif utama:

```bash
yts-dl
```

Perintah:

```bash
yts-dl search [QUERY]
yts-dl top [--genre GENRE] [--min-rating FLOAT] [--quality QUALITY]
yts-dl trending [--quality QUALITY]
yts-dl config setup
yts-dl config show
```

Flag global:

```bash
--remote    # paksa tujuan remote qBittorrent
--local     # paksa tujuan torrent client lokal
--quality   # 720p | 1080p | 1080p.x265 | 2160p | 3D
```

Contoh:

```bash
yts-dl search inception --quality 1080p --remote
yts-dl top --genre action --min-rating 7.5
yts-dl trending --local
```

### Struktur Proyek

```text
yts-dl/
├── main.py              # Entry point CLI dan alur interaktif
├── api.py               # Integrasi YTS API
├── qbit.py              # Client qBittorrent Web API
├── config.py            # Load/save config dan setup wizard
├── ui.py                # Helper Rich (table, panel, spinner)
├── utils.py             # Builder magnet, buka lokal, helper clipboard
├── requirements.txt
└── pyproject.toml
```

### Catatan Operasional

- Jika `--remote` dipakai dan config belum ada, setup wizard akan ditawarkan.
- Jika qBittorrent remote tidak bisa dihubungi, aplikasi bisa menawarkan fallback ke lokal.
- Jika utilitas clipboard tidak tersedia, magnet link akan ditampilkan sebagai fallback.
- Tekan `Ctrl+C` kapan saja untuk keluar dengan aman.

### Troubleshooting

- `command not found: yts-dl`
	- Aktifkan environment atau jalankan `.venv/bin/yts-dl`.
- Gagal koneksi qBittorrent
	- Periksa host URL, kredensial, port, dan akses jaringan.
- Hasil pencarian kosong
	- Coba kata kunci yang lebih umum atau hilangkan filter kualitas.

### Disclaimer

Gunakan aplikasi ini secara bertanggung jawab dan sesuai hukum yang berlaku di wilayah Anda. Anda bertanggung jawab penuh atas konten yang diakses atau diunduh.
