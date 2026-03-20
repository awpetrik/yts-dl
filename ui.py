from __future__ import annotations

from contextlib import contextmanager
from typing import Iterable

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


def show_movie_table(movies: list[dict]) -> None:
    table = Table(title="Daftar Film")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="bold")
    table.add_column("Year", justify="right")
    table.add_column("IMDb ⭐", justify="right")
    table.add_column("Quality", style="green")

    for idx, movie in enumerate(movies, start=1):
        qualities = sorted({t["quality"] for t in movie.get("torrents", []) if t.get("quality")})
        quality_text = ", ".join(qualities) if qualities else "-"
        table.add_row(
            str(idx),
            str(movie.get("title", "-")),
            str(movie.get("year", "-")),
            f"{movie.get('rating', 0):.1f}",
            quality_text,
        )

    console.print(table)


def show_quality_table(torrents: Iterable[dict]) -> None:
    table = Table(title="Pilih Kualitas")
    table.add_column("#", justify="right", style="cyan", no_wrap=True)
    table.add_column("Quality", style="bold green")
    table.add_column("Size")
    table.add_column("Seeds 🌱", justify="right")
    table.add_column("Peers", justify="right")

    for idx, tor in enumerate(torrents, start=1):
        table.add_row(
            str(idx),
            str(tor.get("quality", "-")),
            str(tor.get("size", "-")),
            str(tor.get("seeds", 0)),
            str(tor.get("peers", 0)),
        )

    console.print(table)


def show_success_panel(movie: dict, torrent: dict, destination: str) -> None:
    msg = (
        f"[bold green]Berhasil[/bold green]\n"
        f"{movie.get('title')} ({movie.get('year')}) - {torrent.get('quality')} - {torrent.get('size')}\n"
        f"Seeds: {torrent.get('seeds', 0)} | Peers: {torrent.get('peers', 0)}\n"
        f"Tujuan: {destination}"
    )
    console.print(Panel(msg, border_style="green", title="Sukses"))


def show_error(message: str) -> None:
    console.print(Panel(f"[bold red]{message}[/bold red]", border_style="red", title="Error"))


@contextmanager
def spinner(label: str):
    with console.status(f"[bold cyan]{label}[/bold cyan]"):
        yield
