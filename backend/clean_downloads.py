import os
import shutil
import time
from datetime import timedelta, datetime
from pathlib import Path

import db

downloads = os.getenv("DOWNLOADS_PATH", "downloads")
output = os.getenv("OUTPUTS_PATH", "output")
OUTPUT_CLEAN_INETRVAL_MINUTES = int(os.getenv("OUTPUT_CLEAN_INETRVAL_MINUTES", 60))
DOWNLOADS_CLEAN_INETRVAL_MINUTES = int(os.getenv("DOWNLOADS_CLEAN_INETRVAL_MINUTES", 60))

DOWNLOADS_PATH = Path(downloads)
OUTPUTS_PATH = Path(output)


def remove_old_downloads(hour_ago: datetime):
    older_albums = db.get_albums_older_than(hour_ago)
    print(f"Found {len(older_albums)} albums older than an hour")
    for album in older_albums:
        album_path = DOWNLOADS_PATH / album
        try:
            shutil.rmtree(album_path)
        except FileNotFoundError:
            print(f"Album {album} not found (tried to delete {album_path})")
        db.delete_album(album)
        print(f"Deleted album {album}")
    print("Finished cleaning downloads")


def remove_old_outputs(minutes_ago: datetime):
    for output in OUTPUTS_PATH.iterdir():
        if output.stat().st_mtime < minutes_ago.timestamp():
            output.unlink()
            print(f"Deleted output {output}")
    print("Finished cleaning outputs")


def main():
    print("Starting cleaning service")
    while True:
        time.sleep(5)
        if db.is_table_initialized():
            break
    print("Cleaning service started")
    while True:
        download_minutes = datetime.utcnow() - timedelta(minutes=DOWNLOADS_CLEAN_INETRVAL_MINUTES)
        remove_old_downloads(download_minutes)
        output_minutes = datetime.utcnow() - timedelta(minutes=OUTPUT_CLEAN_INETRVAL_MINUTES)
        remove_old_outputs(output_minutes)
        wait_time = min(DOWNLOADS_CLEAN_INETRVAL_MINUTES, OUTPUT_CLEAN_INETRVAL_MINUTES) * 60
        print(f"Waiting for next cleaning interval, sleeping for {wait_time} seconds")
        time.sleep(wait_time)


if __name__ == '__main__':
    main()
