from __future__ import annotations

from pathlib import Path
from typing import Any
import importlib

from rich.prompt import Confirm, Prompt

from qbit import QBitClient
from ui import spinner, show_error

try:
    tomllib = importlib.import_module("tomllib")
except ModuleNotFoundError:  # pragma: no cover
    tomllib = importlib.import_module("tomli")

CONFIG_DIR = Path.home() / ".config" / "yts-dl"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULT_CONFIG: dict[str, Any] = {
    "local": {"default_mode": "local"},
    "remote": {
        "host": "http://192.168.1.x:8080",
        "username": "admin",
        "password": "",
        "save_path": "/mnt/storage/movies",
    },
}


def config_exists() -> bool:
    return CONFIG_PATH.exists()


def _to_toml(data: dict[str, Any]) -> str:
    local_mode = data.get("local", {}).get("default_mode", "local")
    remote = data.get("remote", {})

    def esc(value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"')

    lines = [
        "[local]",
        f'default_mode = "{esc(str(local_mode))}"',
        "",
        "[remote]",
        f'host = "{esc(str(remote.get("host", "")))}"',
        f'username = "{esc(str(remote.get("username", "")))}"',
        f'password = "{esc(str(remote.get("password", "")))}"',
        f'save_path = "{esc(str(remote.get("save_path", "")))}"',
        "",
    ]
    return "\n".join(lines)


def load_config() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    with CONFIG_PATH.open("rb") as f:
        data = tomllib.load(f)

    merged = DEFAULT_CONFIG.copy()
    merged["local"] = {**DEFAULT_CONFIG["local"], **data.get("local", {})}
    merged["remote"] = {**DEFAULT_CONFIG["remote"], **data.get("remote", {})}
    return merged


def save_config(data: dict[str, Any]) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    toml_text = _to_toml(data)
    CONFIG_PATH.write_text(toml_text, encoding="utf-8")


def run_setup_wizard() -> dict[str, Any]:
    while True:
        host = Prompt.ask("URL host qBittorrent", default="http://192.168.1.x:8080")
        username = Prompt.ask("Username", default="admin")
        password = Prompt.ask("Password", password=True, default="")
        save_path = Prompt.ask("Path simpan default di server", default="/mnt/storage/movies")
        mode = Prompt.ask("Mode default (local/remote)", choices=["local", "remote"], default="local")

        client = QBitClient(host=host, username=username, password=password, save_path=save_path)
        with spinner("Menguji koneksi qBittorrent..."):
            ok = client.test_connection()

        if ok:
            config = {
                "local": {"default_mode": mode},
                "remote": {
                    "host": host,
                    "username": username,
                    "password": password,
                    "save_path": save_path,
                },
            }
            save_config(config)
            return config

        show_error("Koneksi qBittorrent gagal.")
        if not Confirm.ask("Coba lagi?", default=True):
            return load_config()
