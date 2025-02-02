import json
import os
import sqlite3
import threading
from datetime import datetime
from pathlib import Path

db_lock = threading.Lock()

# Initialize SQLite
downloads_folder = Path(os.getenv("DOWNLOADS_PATH", "downloads"))
DB_PATH = str(downloads_folder / "downloads.db")


class AlbumStatus:
    QUEUED = "queued"
    FETCHING_INFO = "fetching info"
    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    ERROR = "error"


def initialize_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS albums (
            uid TEXT PRIMARY KEY,
            insertion_time TEXT DEFAULT CURRENT_TIMESTAMP,
            artist TEXT NOT NULL,
            album TEXT NOT NULL,
            thumbnail TEXT,
            id3 BOOLEAN NOT NULL,
            status TEXT NOT NULL,
            info TEXT NOT NULL
        )
        """)


def insert_album(uid: str, artist: str, album: str, id3: bool):
    print(f"Inserting album {uid}")
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT INTO albums (uid, artist, album, id3, status, info) VALUES (?, ?, ?, ?, ?, '')",
                     (uid, artist, album, id3, AlbumStatus.QUEUED))


def set_album_data(uid: str, total: int, artist: str, album: str, thumbnail: str):
    set_album_status_info(uid, f"0/{total}")
    set_album_artist_and_name(uid, artist, album, thumbnail)


def set_album_status_to_fetching_info(uid: str):
    __update_status(uid, AlbumStatus.FETCHING_INFO)


def set_album_status_to_downloading(uid: str):
    __update_status(uid, AlbumStatus.DOWNLOADING)


def set_album_artist_and_name(uid: str, artist: str, album: str, thumbnail: str):
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE albums SET artist = ?, album = ?, thumbnail = ? WHERE uid = ?",
                     (artist, album, thumbnail, uid))


def set_album_status_to_downloaded(uid: str):
    __update_status(uid, AlbumStatus.DOWNLOADED)


def set_album_status_to_error(uid: str, error_msg: str):
    __update_status(uid, AlbumStatus.ERROR)
    set_album_status_info(uid, error_msg)


def is_album_downloading(uid: str):
    return get_album_status(uid) == AlbumStatus.DOWNLOADING


def is_album_downloaded(uid: str):
    return get_album_status(uid) == AlbumStatus.DOWNLOADED


def __update_status(uid: str, status: str):
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE albums SET status = ? WHERE uid = ?", (status, uid))


def get_album_status(uid: str) -> dict:
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT status FROM albums WHERE uid = ?", (uid,))
        result = cursor.fetchone()
        return json.loads(result[0]) if result else None


def missing_tracks(uid: str, tracks: list[str]):
    print(f"adding to DB Missing tracks for {uid}: {tracks}")
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT info FROM albums WHERE uid = ?", (uid,))
        result = cursor.fetchone()
        if result:
            info = result[0]
            current, total = info.split("/")
            total += "*missing:\n" + "\n".join(tracks)
            conn.execute("UPDATE albums SET info = ? WHERE uid = ?", (f"{current}/{total}", uid))


def increment_album_progress(uid: str):
    print('Incrementing album progress')
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT info FROM albums WHERE uid = ?", (uid,))
        result = cursor.fetchone()
        if result:
            info = result[0]
            current, total = info.split("/")
            current = int(current) + 1
            conn.execute("UPDATE albums SET info = ? WHERE uid = ?", (f"{current}/{total}", uid))


def set_album_status_info(uid: str, info: str):
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE albums SET info = ? WHERE uid = ?", (info, uid))


def get_albums_statuses():
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT uid, artist, album, thumbnail, id3, status, info FROM albums")
        return [{"uid": uid, "artist": artist, "album": album, "thumbnail": thumbnail, "id3": id3, "status": status,
                 "info": info}
                for uid, artist, album, thumbnail, id3, status, info in cursor.fetchall()]


def get_albums_older_than(time: datetime) -> list[str]:
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT uid FROM albums WHERE insertion_time < ?", (time,))
        return [uid for uid, in cursor.fetchall()]


def delete_album(uid: str):
    with db_lock, sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM albums WHERE uid = ?", (uid,))


def is_table_initialized():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='albums'")
        return cursor.fetchone() is not None
