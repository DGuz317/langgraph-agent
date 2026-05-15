from typing import Any


def build_instruction_from_task(task: dict[str, Any]) -> str:
    intent = task.get("intent")
    args = task.get("args") or {}

    if intent == "latest_invoice":
        customer_id = args["customer_id"]
        return f"Get latest invoice for customer_id={customer_id}"

    if intent == "invoices_by_unit_price":
        customer_id = args["customer_id"]
        return f"Get invoices sorted by unit price for customer_id={customer_id}"

    if intent == "tracks_by_artist":
        artist = args["artist"]
        return f"Find tracks by artist {artist}"

    if intent == "albums_by_artist":
        artist = args["artist"]
        return f"Find albums by artist {artist}"

    if intent == "songs_by_genre":
        genre = args["genre"]
        return f"Recommend songs by genre {genre}"

    if intent == "check_song":
        song_title = args["song_title"]
        return f"Check for song {song_title}"

    return task.get("instruction", "")