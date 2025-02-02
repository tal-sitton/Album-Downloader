<div align="center"> 
<h1>Album Downloader</h1>

<img alt="Logo" height="250px" width="250px" src="https://github.com/tal-sitton/Deezer-Album-Downloader/blob/master/frontend/public/icon.png?raw=true"/>

<h3>Music downloader app with a nice UI and a REST API that lets you download every album from Deezer</h3>
</div>

## Features

- **Frontend**: Search by artist, and by album name and downloading music. Track the progress of downloads.
- **Backend**: REST API for interacting with Deezer and managing downloads.
- **Dockerized**: Easily deployable using Docker and Docker Compose.
- **Self-Cleanup**: Uses cron jobs for periodic cleanup of downloads and outputs.

## Prequirement

You'll need a Deezer ARL token.
To Obtain your Arl TokenL

1. login to https://www.deezer.com/
2. F12 → Application → Cookies → "https://www.deezer.com/" → the cookie named "arl"
3. copy the value and write it in the .env file

## Installation

1. Pull the Docker image:
    ```sh
    docker pull ghcr.io/tal-sitton/album-downloader:latest
    ```

2. Create a `.env` file based on the `.env.example` file and fill in the required environment variables:
    ```sh
    cp .env.example .env
    ```

3. Start the Docker container:
   using docker compose:
    ```sh
    docker-compose up
    ```
   or using docker run:
    ```sh
    docker run -d --env-file .env -p 80:80 ghcr.io/tal-sitton/album-downloader:latest
    ```

## Usage

- Access the frontend UI at `http://localhost`.
- Use the search functionality to find artists and albums.
- Download albums and manage your downloads through the UI.

## Screenshots

<img alt="Select Album" height="300px" src="https://github.com/tal-sitton/Deezer-Album-Downloader/blob/master/docs/Select Album.png?raw=true"/>
<img alt="Select Album" height="300px" src="https://github.com/tal-sitton/Deezer-Album-Downloader/blob/master/docs/Download Album.png?raw=true"/>

## API Endpoints

- `GET /api/artists?name={name}`: Search for artists by name.
- `GET /api/albums?artist_id={artist_id}`: Get albums for a specific artist.
- `POST /api/download_album/{album_id}`: Download an album by its ID.
- `GET /api/album_status/`: Get the status of all albums being downloaded.
- `WS /api/albums_status`: Websocket endpoint for tracking album download progress.
- `GET /api/zip_downloaded_albums?uids={uids}`: Zip downloaded albums and serve them.
- `GET /api/output/{zip_name}`: Download the zipped albums.

## Environment Variables

- `ARL`: Deezer ARL token for authentication. (see [Prequirement](#prequirement))
- `TRACKS_DOWNLOAD_MAX_WORKERS`: Maximum number of workers for downloading tracks.
- `DOWNLOADS_PATH`: Path to the downloads directory.
- `OUTPUTS_PATH`: Path to the outputs directory.
- `ALBUMS_DOWNLOAD_MAX_WORKERS`: Maximum number of workers for downloading albums.
- `STATUS_UPDATE_INTERVAL`: Interval for updating the status of downloads in the websocket.
- `OUTPUT_CLEAN_INTERVAL_MINUTES`: Interval for cleaning the outputs directory.
- `DOWNLOADS_CLEAN_INTERVAL_MINUTES`: Interval for cleaning the downloads directory.
