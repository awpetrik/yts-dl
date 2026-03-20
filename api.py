from __future__ import annotations

from typing import Any

import requests

BASE_URL = "https://movies-api.accel.li/api/v2"
TIMEOUT = 15


class YTSAPIError(Exception):
    """Raised when YTS API request fails."""


def _request(endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{BASE_URL}/{endpoint}"
    try:
        response = requests.get(url, params=params or {}, timeout=TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise YTSAPIError(f"Gagal menghubungi API YTS: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise YTSAPIError("Respons API tidak valid (bukan JSON).") from exc

    status = payload.get("status")
    if status != "ok":
        message = payload.get("status_message", "Terjadi kesalahan pada API.")
        raise YTSAPIError(f"API YTS error: {message}")

    return payload.get("data", {})


def _normalize_movie(movie: dict[str, Any]) -> dict[str, Any]:
    torrents = []
    for item in movie.get("torrents", []):
        torrents.append(
            {
                "quality": item.get("quality", "-") ,
                "size": item.get("size", "-") ,
                "seeds": int(item.get("seeds", 0) or 0),
                "peers": int(item.get("peers", 0) or 0),
                "hash": item.get("hash", ""),
            }
        )

    return {
        "id": movie.get("id"),
        "title": movie.get("title", "Unknown"),
        "year": movie.get("year", 0),
        "rating": float(movie.get("rating", 0) or 0),
        "torrents": torrents,
    }


def search_movies(
    query: str,
    limit: int = 5,
    quality: str | None = None,
    genre: str | None = None,
    min_rating: float = 0,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "query_term": query,
        "limit": limit,
        "minimum_rating": min_rating,
    }
    if quality:
        params["quality"] = quality
    if genre:
        params["genre"] = genre

    data = _request("list_movies.json", params)
    movies = data.get("movies") or []
    return [_normalize_movie(movie) for movie in movies]


def get_top_movies(
    limit: int = 5,
    genre: str | None = None,
    min_rating: float = 0,
    quality: str | None = None,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "sort_by": "rating",
        "limit": limit,
        "minimum_rating": min_rating,
    }
    if genre:
        params["genre"] = genre
    if quality:
        params["quality"] = quality

    data = _request("list_movies.json", params)
    movies = data.get("movies") or []
    return [_normalize_movie(movie) for movie in movies]


def get_trending(limit: int = 5, quality: str | None = None) -> list[dict[str, Any]]:
    params: dict[str, Any] = {"sort_by": "date_added", "limit": limit}
    if quality:
        params["quality"] = quality

    data = _request("list_movies.json", params)
    movies = data.get("movies") or []
    return [_normalize_movie(movie) for movie in movies]


def get_movie_detail(movie_id: int) -> dict[str, Any]:
    params = {"movie_id": movie_id, "with_images": "false", "with_cast": "false"}
    data = _request("movie_details.json", params)
    movie = data.get("movie") or {}
    return _normalize_movie(movie)
