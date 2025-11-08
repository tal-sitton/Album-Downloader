<div align="center"> 
<h1>Album Downloader</h1>

<img alt="Logo" height="250px" width="250px" src="https://github.com/tal-sitton/Deezer-Album-Downloader/blob/master/frontend/public/icon.png?raw=true"/>

<h3>Music downloader app with a nice UI and a REST API that lets you download every album from Deezer</h3>
</div>

## Features

- **Frontend**: Search by artist, and by album name and downloading music. Track the progress of downloads.
- **Backend**: REST API for interacting with Deezer and managing downloads.
- **Dockerized**: Easily deployable using Docker and Docker Compose.
- **Self-Cleanup**: Periodic cleanup of downloads and outputs.

## Prequirement

You'll need a Deezer ARL token.
After running the ui, to Obtain your Arl Token:

1. Using the UI, hit `Renew`, this will open Deezer account activation in a new tab.
2. Verify → F12 → Application → Cookies → "https://www.deezer.com/" → the cookie named "arl"
3. copy the value and write it in the text box.

## Installation

1. create `config` directory, and inside `arls.txt`
    ```sh
    mkdir config
    touch config/arls.txt
    ```
### Docker compose

2. copy `docker-compose.prod.yml` to `docker-compose.yml`:
    ```sh
    cp docker-compose.prod.yml docker-compose.yml
    ```
   
3. Start the Docker container:
    ```sh
    docker-compose up -d
    ```

### Docker run
2. using docker run:
    ```sh
    docker run -d -v ./config/arls.txt:/app/config/arls.txt -p 80:80 ghcr.io/tal-sitton/album-downloader:latest
    ```

## Usage

- Access the frontend UI at `http://localhost`.
- Add new ARL tokens using the UI.
- Use the search functionality to find artists and albums.
- Download albums and manage your downloads through the UI.

## Screenshots

<img alt="Select Album" height="300px" src="https://github.com/tal-sitton/Deezer-Album-Downloader/blob/master/docs/Select Album.png?raw=true"/>
<img alt="Select Album" height="300px" src="https://github.com/tal-sitton/Deezer-Album-Downloader/blob/master/docs/Download Album.png?raw=true"/>

## API Endpoints

#### ARLs
- `GET /api/arl/new`: Generate a new Deezer account. Return Verify URL.
- `GET /api/arl/count`: Get the count of available ARL tokens.
- `POST /api/arl/renew_arl`: Add a new ARL token to the pool.

#### Search & Download
- `GET /api/artists?name={name}`: Search for artists by name.
- `GET /api/albums?artist_id={artist_id}`: Get albums for a specific artist.
- `POST /api/download_album/{album_id}`: Download an album by its ID.
- `GET /api/album_status/`: Get the status of all albums being downloaded.
- `WS /api/albums_status`: Websocket endpoint for tracking album download progress.
- `GET /api/zip_downloaded_albums?uids={uids}`: Zip downloaded albums and serve them.
- `GET /api/output/{zip_name}`: Download the zipped albums.
- `POST /api/clean`: Clean all downloads.

## Environment Variables

- `TRACKS_DOWNLOAD_MAX_WORKERS`: Maximum number of workers for downloading tracks.
- `DOWNLOADS_PATH`: Path to the downloads directory.
- `OUTPUTS_PATH`: Path to the outputs directory.
- `ALBUMS_DOWNLOAD_MAX_WORKERS`: Maximum number of workers for downloading albums.
- `STATUS_UPDATE_INTERVAL`: Interval for updating the status of downloads in the websocket.
- `OUTPUT_CLEAN_INTERVAL_MINUTES`: Interval for cleaning the outputs directory.
- `DOWNLOADS_CLEAN_INTERVAL_MINUTES`: Interval for cleaning the downloads directory.
