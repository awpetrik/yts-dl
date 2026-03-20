# yts-dl

CLI interaktif untuk mencari film dari API YTS dan mengirim torrent ke client lokal atau qBittorrent remote.

## Jalankan langsung

```bash
python main.py
```

## Install editable

```bash
pip install -e .
```

## Command utama

```bash
yts-dl
yts-dl search [QUERY]
yts-dl top [--genre GENRE] [--min-rating 7.5] [--quality 1080p]
yts-dl trending [--quality 720p]
yts-dl config setup
yts-dl config show
```
