from __future__ import annotations

from typing import Callable

import click
from rich.prompt import Confirm, Prompt

from api import YTSAPIError, get_top_movies, get_trending, search_movies
from config import config_exists, load_config, run_setup_wizard
from qbit import QBitClient
from ui import console, show_error, show_movie_table, show_quality_table, show_success_panel, spinner
from utils import build_magnet, copy_to_clipboard, open_magnet

QUALITY_CHOICES = ["720p", "1080p", "1080p.x265", "2160p", "3D"]


class BackAction(Exception):
    pass


def fetch_with_retry(loader: Callable[[], list[dict]], label: str) -> list[dict]:
    while True:
        try:
            with spinner(label):
                return loader()
        except YTSAPIError as exc:
            show_error(str(exc))
            if not Confirm.ask("Coba lagi?", default=True):
                return []


def pick_movie(movies: list[dict]) -> dict | None:
    if not movies:
        return None

    show_movie_table(movies)
    while True:
        choices = [str(i) for i in range(1, len(movies) + 1)] + ["b"]
        selected = Prompt.ask(
            f"Pilih film [1-{len(movies)}] atau (b)ack",
            choices=choices,
            default="b",
        )
        if selected == "b":
            return None
        return movies[int(selected) - 1]


def pick_quality(movie: dict, forced_quality: str | None = None) -> dict:
    torrents = movie.get("torrents", [])
    if not torrents:
        raise BackAction("Film tidak memiliki torrent yang tersedia.")

    if forced_quality:
        for tor in torrents:
            if tor.get("quality", "").lower() == forced_quality.lower():
                return tor

        available = ", ".join([t.get("quality", "-") for t in torrents])
        raise BackAction(f"Kualitas '{forced_quality}' tidak tersedia. Pilihan: {available}")

    console.print(
        f"\n[bold]{movie.get('title')} ({movie.get('year')})[/bold] - IMDb {movie.get('rating', 0):.1f}"
    )
    show_quality_table(torrents)

    while True:
        choices = [str(i) for i in range(1, len(torrents) + 1)] + ["b"]
        selected = Prompt.ask(
            f"Pilih kualitas [1-{len(torrents)}] atau (b)ack",
            choices=choices,
            default="b",
        )
        if selected == "b":
            raise BackAction("Kembali")
        return torrents[int(selected) - 1]


def pick_destination(config: dict, force_local: bool, force_remote: bool) -> str | None:
    if force_local:
        return "local"
    if force_remote:
        return "remote"

    default_mode = config.get("local", {}).get("default_mode", "local")
    default_choice = "2" if default_mode == "remote" else "1"

    console.print("\n1. Open di local torrent client")
    console.print("2. Send ke remote qBittorrent (homelab)")
    console.print("3. Copy magnet link ke clipboard")

    selected = Prompt.ask("Pilih [1-3]", choices=["1", "2", "3", "b"], default=default_choice)
    if selected == "b":
        return None
    mapping = {"1": "local", "2": "remote", "3": "clipboard"}
    return mapping[selected]


def do_action(destination: str, magnet_url: str, config: dict) -> bool:
    if destination == "local":
        return open_magnet(magnet_url)

    if destination == "clipboard":
        return copy_to_clipboard(magnet_url)

    remote = config.get("remote", {})
    client = QBitClient(
        host=remote.get("host", ""),
        username=remote.get("username", ""),
        password=remote.get("password", ""),
        save_path=remote.get("save_path", ""),
    )
    return client.add_torrent(magnet_url)


def ensure_remote_config(config: dict) -> dict:
    remote = config.get("remote", {})
    if not remote.get("host") or remote.get("host") == "http://192.168.1.x:8080":
        console.print("[yellow]Konfigurasi remote belum lengkap.[/yellow]")
        return run_setup_wizard()
    return config


def prepare_config(force_remote: bool) -> dict:
    if force_remote and not config_exists():
        console.print("[yellow]Konfigurasi belum ditemukan. Jalankan setup remote dulu.[/yellow]")
        return run_setup_wizard()
    return load_config()


def movie_flow(
    movies: list[dict],
    config: dict,
    force_local: bool,
    force_remote: bool,
    quality: str | None,
) -> bool:
    while True:
        movie = pick_movie(movies)
        if not movie:
            return True

        while True:
            try:
                torrent = pick_quality(movie, quality)
            except BackAction as exc:
                if str(exc) == "Kembali":
                    break
                show_error(str(exc))
                if quality:
                    break
                continue

            while True:
                destination = pick_destination(config, force_local, force_remote)
                if not destination:
                    if force_local or force_remote:
                        return True
                    break

                if destination == "remote":
                    config = ensure_remote_config(config)

                console.print(
                    f"\n[green]✔[/green] {movie.get('title')} ({movie.get('year')}) - {torrent.get('quality')} - {torrent.get('size')}"
                )
                console.print(f"Seeds: {torrent.get('seeds', 0)} | Peers: {torrent.get('peers', 0)}")

                if not Confirm.ask("Lanjut?", default=True):
                    break

                magnet = build_magnet(torrent.get("hash", ""), f"{movie.get('title')} ({movie.get('year')})")
                ok = do_action(destination, magnet, config)

                if not ok:
                    if destination == "remote":
                        show_error("qBittorrent tidak bisa dihubungi.")
                        if Confirm.ask("Buka di local torrent client saja?", default=True):
                            if open_magnet(magnet):
                                show_success_panel(movie, torrent, "Local")
                                return Confirm.ask("Cari film lain?", default=True)
                        break

                    if destination == "clipboard":
                        show_error("Gagal menyalin ke clipboard. Ini link magnet Anda:")
                        console.print(magnet)
                        return Confirm.ask("Cari film lain?", default=True)

                    show_error("Gagal membuka torrent client lokal.")
                    break

                dest_name = {"local": "Local", "remote": "Remote qBittorrent", "clipboard": "Clipboard"}[destination]
                show_success_panel(movie, torrent, dest_name)
                return Confirm.ask("Cari film lain?", default=True)

            if not (force_local or force_remote):
                continue
            break


def run_main_menu(force_local: bool, force_remote: bool, quality: str | None) -> None:
    config = prepare_config(force_remote)

    while True:
        console.print("\n[bold cyan]🎬  YTS Downloader[/bold cyan]")
        console.print("[dim]──────────────────[/dim]")
        console.print("1. Search movie")
        console.print("2. Top movies")
        console.print("3. Trending (latest)")
        console.print("4. Exit")

        choice = Prompt.ask("Pilih [1-4]", choices=["1", "2", "3", "4"], default="1")

        if choice == "4":
            break

        if choice == "1":
            query = Prompt.ask("Search").strip()
            if not query:
                show_error("Kata kunci tidak boleh kosong.")
                continue

            movies = fetch_with_retry(lambda: search_movies(query=query, limit=5), "Mencari film...")
            if not movies:
                show_error(f"Tidak ada hasil untuk '{query}'")
                continue

            if not movie_flow(movies, config, force_local, force_remote, quality):
                break

        if choice == "2":
            movies = fetch_with_retry(lambda: get_top_movies(limit=5), "Mengambil top movies...")
            if not movies:
                show_error("Tidak ada data top movies.")
                continue
            if not movie_flow(movies, config, force_local, force_remote, quality):
                break

        if choice == "3":
            movies = fetch_with_retry(lambda: get_trending(limit=5), "Mengambil trending movies...")
            if not movies:
                show_error("Tidak ada data trending.")
                continue
            if not movie_flow(movies, config, force_local, force_remote, quality):
                break


@click.group(invoke_without_command=True)
@click.option("--remote", "force_remote", is_flag=True, help="Kirim ke qBittorrent remote")
@click.option("--local", "force_local", is_flag=True, help="Buka di torrent client local")
@click.option("--quality", "global_quality", type=click.Choice(QUALITY_CHOICES), help="Pilih kualitas default")
@click.pass_context
def cli(ctx: click.Context, force_remote: bool, force_local: bool, global_quality: str | None) -> None:
    if force_local and force_remote:
        raise click.ClickException("Tidak bisa memakai --local dan --remote bersamaan.")

    ctx.ensure_object(dict)
    ctx.obj["force_remote"] = force_remote
    ctx.obj["force_local"] = force_local
    ctx.obj["quality"] = global_quality

    try:
        if ctx.invoked_subcommand is None:
            run_main_menu(force_local=force_local, force_remote=force_remote, quality=global_quality)
    except KeyboardInterrupt:
        console.print("\nSampai jumpa! 👋")


@cli.command()
@click.argument("query", required=False)
@click.option("--quality", "cmd_quality", type=click.Choice(QUALITY_CHOICES), help="Filter kualitas")
@click.pass_context
def search(ctx: click.Context, query: str | None, cmd_quality: str | None) -> None:
    try:
        query_value = query or Prompt.ask("Search").strip()
        if not query_value:
            show_error("Kata kunci tidak boleh kosong.")
            return

        quality = cmd_quality or ctx.obj.get("quality")
        movies = fetch_with_retry(
            lambda: search_movies(query=query_value, limit=5, quality=quality),
            "Mencari film...",
        )
        if not movies:
            show_error(f"Tidak ada hasil untuk '{query_value}'")
            return

        config = prepare_config(ctx.obj.get("force_remote", False))
        movie_flow(
            movies=movies,
            config=config,
            force_local=ctx.obj.get("force_local", False),
            force_remote=ctx.obj.get("force_remote", False),
            quality=quality,
        )
    except KeyboardInterrupt:
        console.print("\nSampai jumpa! 👋")


@cli.command()
@click.option("--genre", default=None, help="Filter genre")
@click.option("--min-rating", default=0.0, type=float, help="Minimum rating")
@click.option("--quality", "cmd_quality", type=click.Choice(QUALITY_CHOICES), help="Filter kualitas")
@click.pass_context
def top(ctx: click.Context, genre: str | None, min_rating: float, cmd_quality: str | None) -> None:
    try:
        quality = cmd_quality or ctx.obj.get("quality")
        movies = fetch_with_retry(
            lambda: get_top_movies(limit=5, genre=genre, min_rating=min_rating, quality=quality),
            "Mengambil top movies...",
        )
        if not movies:
            show_error("Tidak ada data top movies.")
            return

        config = prepare_config(ctx.obj.get("force_remote", False))
        movie_flow(
            movies=movies,
            config=config,
            force_local=ctx.obj.get("force_local", False),
            force_remote=ctx.obj.get("force_remote", False),
            quality=quality,
        )
    except KeyboardInterrupt:
        console.print("\nSampai jumpa! 👋")


@cli.command()
@click.option("--quality", "cmd_quality", type=click.Choice(QUALITY_CHOICES), help="Filter kualitas")
@click.pass_context
def trending(ctx: click.Context, cmd_quality: str | None) -> None:
    try:
        quality = cmd_quality or ctx.obj.get("quality")
        movies = fetch_with_retry(
            lambda: get_trending(limit=5, quality=quality),
            "Mengambil trending movies...",
        )
        if not movies:
            show_error("Tidak ada data trending.")
            return

        config = prepare_config(ctx.obj.get("force_remote", False))
        movie_flow(
            movies=movies,
            config=config,
            force_local=ctx.obj.get("force_local", False),
            force_remote=ctx.obj.get("force_remote", False),
            quality=quality,
        )
    except KeyboardInterrupt:
        console.print("\nSampai jumpa! 👋")


@cli.group()
def config() -> None:
    """Kelola konfigurasi aplikasi."""


@config.command("setup")
def config_setup() -> None:
    try:
        run_setup_wizard()
        console.print("[green]Konfigurasi berhasil disimpan.[/green]")
    except KeyboardInterrupt:
        console.print("\nSampai jumpa! 👋")


@config.command("show")
def config_show() -> None:
    data = load_config()
    console.print(data)


if __name__ == "__main__":
    cli()
