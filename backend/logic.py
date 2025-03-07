import concurrent
import copy
import json
import os
import shutil
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import requests
from deemix.downloader import Downloader
from deemix.types.DownloadObjects import Single
from deezer import Deezer, TrackFormats
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3

import db
from models import Artist, BasicAlbum
from models import DeezerAlbum, DeezerTrack
from utils import sanitize_filename

BITRATE = TrackFormats.MP3_128

config_path = Path.cwd() / "config"
with open(config_path / "config.json") as f:
    SETTINGS = json.load(f)

ARL = os.getenv("ARL")
if not ARL:
    with open(config_path / ".arl") as f:
        ARL = f.read()

tracks_download_max_workers = int(os.getenv("TRACKS_DOWNLOAD_MAX_WORKERS", 5))
EXECUTOR = ThreadPoolExecutor(max_workers=tracks_download_max_workers)
dz = Deezer()
dz.login_via_arl(ARL)


def get_artists(name: str) -> list[Artist]:
    print(f"Getting artists with name {name}")
    raw_artists = dz.api.search_artist(name)
    artists = [Artist(**artist) for artist in raw_artists["data"]]
    return artists


def get_albums(artist_id: str) -> list[DeezerAlbum]:
    print(f"Getting albums from artist {artist_id}")
    raw_albums = []
    artist = Artist(**dz.api.get_artist(artist_id))
    while True:
        response = dz.api.get_artist_albums(artist_id, index=len(raw_albums))
        raw_albums.extend(response["data"])
        if "limit=-1&index=-1" in response.get("next"):
            break
    albums = [DeezerAlbum(**album, artist=artist) for album in raw_albums]
    return albums


def download_album(album_id: str, download_path: Path, uid: str, id3: bool):
    db.insert_album(uid, "", "", id3)
    try:
        download_folder = download_path / uid
        download_folder.mkdir(parents=True, exist_ok=True)
        album = get_album_info(album_id)
        db.set_album_data(uid, album.total_tracks, album.artist.name, album.name, album.image)
        db.set_album_status_to_fetching_info(uid)
        __download_album(album, download_folder, uid, id3)
        print(f"Albums downloaded to {download_folder}")
        db.set_album_status_to_downloaded(uid)
    except Exception as e:
        print(f"Error downloading album: {e}")
        db.set_album_status_to_error(uid, str(e))
        raise e


def __download_album(album: BasicAlbum, download_path: Path, uid: str, id3: bool):
    print(f"Downloading album {album.name}")
    artist_name = album.artist.name
    album_output_path = download_path / sanitize_filename(artist_name) / sanitize_filename(album.name)

    db.set_album_status_to_downloading(uid)
    settings = copy.deepcopy(SETTINGS)
    settings["downloadLocation"] = str(album_output_path)

    tasks = []
    for track in album.tracks:
        tasks.append(EXECUTOR.submit(__download_track, track, settings, uid))

    for future in concurrent.futures.as_completed(tasks):
        future.result()

    print("All tracks downloaded")

    album_cover = __download_album_cover(album, download_path)
    __format_files(album, album_output_path, download_path, id3, album_cover)


def __download_track(track: DeezerTrack, settings: dict, uid: str):
    print(f"Downloading track {track.name}")

    trackAPI = {
        "id": track.id,
        "title": track.name,
        "artist": {"name": track.artists[0]}
    }
    obj = Single({
        "type": "track",
        "id": track.id,
        "bitrate": BITRATE,
        "title": track.name,
        "artist": track.artists[0],
        "cover": None,
        'single': {
            'trackAPI': trackAPI,
            'albumAPI': None
        }
    })

    # listener = LogListener()
    Downloader(dz, obj, settings, None).start()
    db.increment_album_progress(uid)
    print(f"Track {track.name} downloaded")


def __format_files(album: BasicAlbum, album_output_path: Path, download_path: Path, id3: bool, album_cover: Path):
    print(f"Formatting files for album {album.name}")
    if id3:
        album_cover_data = open(album_cover, "rb").read()
        album_apic = APIC(encoding=0, mime="image/jpeg", type=3, desc=u"Cover", data=album_cover_data)
    for track in album.tracks:
        try:
            title = sanitize_filename(track.name)
            file = album_output_path / f"{track.id}.mp3"
            artist = sanitize_filename(album.artist.name)
            album_title = sanitize_filename(album.name)
            release_date = datetime.fromtimestamp(album.release_date_epoch).strftime('%Y-%m-%d')
            if id3:
                audio = MP3(file, ID3=ID3)
                if audio.tags is None:
                    audio.add_tags()
                audio.tags.add(album_apic)
                audio.save()
                audio_easy = EasyID3(file)
                audio_easy["artist"] = artist
                audio_easy["title"] = title
                audio_easy["tracknumber"] = str(track.track_number)
                audio_easy["album"] = album_title
                audio_easy["date"] = release_date
                audio_easy.save()
                new_name = title + ".mp3"
            else:
                new_name = f"{artist} --- {album_title} --- {track.track_number} --- {release_date} --- {title}.mp3"
            file.rename(download_path / new_name)
        except FileNotFoundError as e:
            print(f"Error formatting file {track.name}: {e}")
    album_output_path.rmdir()
    artist_path = album_output_path.parent
    if not list(artist_path.iterdir()):
        artist_path.rmdir()


def __download_album_cover(album: BasicAlbum, download_path: Path) -> Path:
    album_cover = requests.get(album.image).content
    album_cover_name = f"{sanitize_filename(album.artist.name)} --- {sanitize_filename(album.name)} --- cover.jpg"
    album_cover_path = download_path / album_cover_name
    with open(album_cover_path, "wb") as f:
        f.write(album_cover)
    return album_cover_path


def get_album_info(album_id: str) -> DeezerAlbum:
    raw_album = dz.api.get_album(album_id)
    raw_album["tracks"] = dz.api.get_album_tracks(album_id)
    album = DeezerAlbum(**raw_album)
    print(f"Got album {album.name}")
    return album


def compress_albums(uids: list[str], download_path: Path, outputs_path: Path, zip_name: str) -> Path:
    """
    copy the downloaded uids to the tmp folder, zip them to output_path, and delete the tmp folder
    """
    output_path = outputs_path / zip_name
    processing_path = Path("processing") / zip_name
    processing_path.mkdir(parents=True, exist_ok=True)

    for uid in uids:
        download_folder = download_path / uid
        for file in download_folder.iterdir():
            shutil.copy(file, processing_path / file.name)
    shutil.make_archive(str(output_path), 'zip', processing_path)
    shutil.rmtree(processing_path)
    return output_path


if __name__ == '__main__':
    download_album("264854952", Path("downloads"), "test3")
