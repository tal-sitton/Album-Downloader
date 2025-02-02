import ArtistSearch from "./ArtistSearch";
import AlbumSearch from "./AlbumSearch";
import DownloadButton from "./DownloadButton";
import React, {useState} from "react";
import {Stack, Switch, Typography} from "@mui/material";

const SearchToDownload: React.FC = () => {
    const [selectedArtist, setSelectedArtist] = useState<string | null>(null);
    const [selectedAlbum, setSelectedAlbum] = useState<string | null>(null);
    const [selectedId3, setSelectedId3] = useState<boolean>(false);

    return <>
        <ArtistSearch onSelectArtist={setSelectedArtist}/>
        <AlbumSearch artistId={selectedArtist} onSelectAlbum={setSelectedAlbum}/>
        <Stack direction="row" sx={{alignItems: 'center', justifyContent: "center"}}>
            <Typography>File Name</Typography>
            <Switch
                checked={selectedId3}
                onChange={(event) => setSelectedId3(event.target.checked)}
            />
            <Typography>ID3</Typography>
        </Stack>
        <DownloadButton albumId={selectedAlbum} id3={selectedId3}/>
    </>
}

export default SearchToDownload;
