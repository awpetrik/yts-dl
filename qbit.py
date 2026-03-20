from __future__ import annotations

import requests


class QBitClient:
    def __init__(self, host: str, username: str, password: str, save_path: str) -> None:
        self.host = host.rstrip("/")
        self.username = username
        self.password = password
        self.save_path = save_path
        self.session = requests.Session()

    def login(self) -> bool:
        try:
            response = self.session.post(
                f"{self.host}/api/v2/auth/login",
                data={"username": self.username, "password": self.password},
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException:
            return False

        return response.text.strip() == "Ok."

    def logout(self) -> bool:
        try:
            response = self.session.post(f"{self.host}/api/v2/auth/logout", timeout=10)
            response.raise_for_status()
            return True
        except requests.RequestException:
            return False

    def add_torrent(self, magnet_url: str) -> bool:
        if not self.login():
            return False

        try:
            response = self.session.post(
                f"{self.host}/api/v2/torrents/add",
                data={"urls": magnet_url, "savepath": self.save_path},
                timeout=10,
            )
            response.raise_for_status()
            result = response.text.strip().lower()
            return result in {"ok.", "ok"} or response.status_code == 200
        except requests.RequestException:
            return False
        finally:
            self.logout()

    def test_connection(self) -> bool:
        ok = self.login()
        if ok:
            self.logout()
        return ok
