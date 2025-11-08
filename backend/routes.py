import asyncio
import os
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, BackgroundTasks, APIRouter
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from starlette.staticfiles import StaticFiles
from starlette.websockets import WebSocket

import clean_downloads
import db
import logic
from models import Artist, BasicAlbum

db.initialize_db()

api_router = APIRouter(prefix="/api")

app = FastAPI()

downloads = os.getenv("DOWNLOADS_PATH", "downloads")
output = os.getenv("OUTPUTS_PATH", "output")
albums_download_max_workers = int(os.getenv("ALBUMS_DOWNLOAD_MAX_WORKERS", 5))
STATUS_UPDATE_INTERVAL = int(os.getenv("STATUS_UPDATE_INTERVAL", 5))

DOWNLOADS_PATH = Path(downloads)
OUTPUTS_PATH = Path(output)

DOWNLOADS_PATH.mkdir(parents=True, exist_ok=True)
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)

executor = ThreadPoolExecutor(max_workers=albums_download_max_workers)

@api_router.get("/arl/new")
async def arl_status() -> str:
    status = logic.generate_new_arl()
    return status

@api_router.get("/arl/count")
async def arls_count() -> int:
    status = logic.count_arls()
    return status

class ARLRenewRequest(BaseModel):
    arl: str

@api_router.post("/arl/renew")
async def renew_arl(arl: ARLRenewRequest):
    logic.renew_arl(arl.arl)

@api_router.get("/artists")
async def get_artists(name: str) -> list[Artist]:
    artists = logic.get_artists(name)
    return artists


@api_router.get("/albums")
async def get_albums(artist_id: str) -> list[BasicAlbum]:
    """
    Get albums from an artist id retrieved from get_artists
    """
    albums = logic.get_albums(artist_id)
    return albums


@api_router.post("/download_album/{album_id}")
async def download_albums(album_id: str, id3: bool = False) -> str:
    """
    Download an album from an album id retrieved from get_albums
    :param album_id: The album id
    :param id3: Whether to add id3 tags to the tracks
    :return: uid of the download
    """
    loop = asyncio.get_running_loop()
    uid = uuid.uuid4().hex
    loop.run_in_executor(executor, logic.download_album, album_id, DOWNLOADS_PATH, uid, id3)
    return uid


@api_router.get("/album_status")
async def album_status() -> list[dict]:
    """
    Get the status of all albums that is are being downloaded
    :return: The status of the albums in format
        {uid: "uuid", artist: "artist Name", album: "album Name",thumbnail:"http://image.jpg", status: "downloading", info: "1/3"}
    """
    status = db.get_albums_statuses()
    return status


@api_router.websocket("/albums_status")
async def albums_status(websocket: WebSocket):
    await websocket.accept()
    while True:
        statuses = db.get_albums_statuses()
        statuses = [{**status, "id3": bool(status.get("id3"))} for status in statuses]
        try:
            await websocket.send_json(statuses)
        except Exception as e:
            print(e)
            try:
                await websocket.close()
            finally:
                break
        await asyncio.sleep(STATUS_UPDATE_INTERVAL)


@api_router.get("/zip_downloaded_albums")
async def zip_downloaded_albums(uids: str) -> str:
    """
    Zip the downloaded albums and serve them in /output
    :param uids: A list of album uids to zip
    :return: The name of the zip file
    """
    parsed_uids = uids.split(",")
    zip_name = uuid.uuid4().hex
    logic.compress_albums(parsed_uids, DOWNLOADS_PATH, OUTPUTS_PATH, zip_name)
    return zip_name


@api_router.post("/clean")
async def clean_all():
    clean_downloads.remove_old_downloads(datetime.utcnow())
    clean_downloads.remove_old_outputs(datetime.utcnow())
    return "Downloads cleaned"


async def delete_zip(zip: Path):
    await asyncio.sleep(60)
    zip.unlink()
    print(f"Zip file {zip} has been deleted")


@api_router.get("/output/{zip_name}", response_class=FileResponse)
async def get_zip(zip_name: str, background_tasks: BackgroundTasks):
    file = OUTPUTS_PATH / f"{zip_name}.zip"
    background_tasks.add_task(delete_zip, file)
    return FileResponse(file, media_type='application/zip', filename=file.name)


app.include_router(api_router)
if Path("static").exists():
    app.mount("/", StaticFiles(directory="static", html=True), name="static")
