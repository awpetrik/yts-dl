from __future__ import annotations

import platform
import subprocess
from urllib.parse import quote_plus


def build_magnet(hash_value: str, title: str) -> str:
    encoded_title = quote_plus(title)
    return (
        f"magnet:?xt=urn:btih:{hash_value}&dn={encoded_title}"
        "&tr=udp://tracker.opentrackr.org:1337/announce"
        "&tr=udp://tracker.torrent.eu.org:451/announce"
        "&tr=udp://open.stealth.si:80/announce"
    )


def open_magnet(magnet_url: str) -> bool:
    system_name = platform.system().lower()
    try:
        if system_name == "darwin":
            subprocess.run(["open", magnet_url], check=True)
        elif system_name == "linux":
            subprocess.run(["xdg-open", magnet_url], check=True)
        elif system_name == "windows":
            subprocess.run(["cmd", "/c", "start", "", magnet_url], check=True)
        else:
            return False
        return True
    except Exception:
        return False


def copy_to_clipboard(text: str) -> bool:
    system_name = platform.system().lower()

    try:
        if system_name == "darwin":
            subprocess.run(["pbcopy"], input=text, text=True, check=True)
            return True
        if system_name == "linux":
            for cmd in (["xclip", "-selection", "clipboard"], ["xsel", "--clipboard", "--input"]):
                try:
                    subprocess.run(cmd, input=text, text=True, check=True)
                    return True
                except Exception:
                    continue
        if system_name == "windows":
            subprocess.run(["clip"], input=text, text=True, check=True)
            return True
    except Exception:
        return False

    return False
