import React, {useState} from 'react';
import {
    Avatar,
    Box,
    CircularProgress,
    InputAdornment,
    List,
    ListItem,
    ListItemAvatar,
    ListItemText,
    TextField
} from '@mui/material';
import {Album, useFetchAlbums} from '../api/api';
import ExplicitIcon from '@mui/icons-material/Explicit';

interface AlbumSearchProps {
    artistId: string | null;
    onSelectAlbum: (albumId: string) => void;
}

const AlbumSearch: React.FC<AlbumSearchProps> = ({artistId, onSelectAlbum}) => {
    const [showResults, setShowResults] = useState<boolean>(true);
    const [selectedAlbum, setSelectedAlbum] = useState<Album | null>(null);
    const [search, setSearch] = useState<string>('');
    const {data: albums, isLoading} = useFetchAlbums(artistId || '');

    if (!artistId) {
        if (selectedAlbum) {
            onSelectAlbum('');
            setSelectedAlbum(null);
        }
        if (search) {
            setSearch('');
        }
        if (!showResults) {
            setShowResults(true);
        }
        return null;
    }

    const handleAlbumSelect = (album: Album) => {
        setSelectedAlbum(album);
        onSelectAlbum(album.id);
        setShowResults(false); // Collapse results
    };

    const handleInputChange = (value: string) => {
        setSearch(value);
        setSelectedAlbum(null);
        onSelectAlbum('');
        setShowResults(true);
    }

    return (
        <Box sx={{width: '100%', maxWidth: 600, mx: 'auto', mb: 4}}>
            <TextField
                label="Search Album"
                fullWidth
                value={selectedAlbum ? selectedAlbum.name : search}
                onChange={(e) => handleInputChange(e.target.value)}
                slotProps={{
                    input: {
                        startAdornment: selectedAlbum && (
                            <InputAdornment position="start">
                                <Avatar src={selectedAlbum.image} alt={selectedAlbum.name}
                                        sx={{width: 32, height: 32}}/>
                            </InputAdornment>
                        ),
                    },
                }}
                sx={{mb: 2}}
            />
            {isLoading && <CircularProgress/>}
            {showResults && (
                <List>
                    {albums?.map((album: Album) => (
                        album.name.toLowerCase().includes(search.toLowerCase()) &&
                        <ListItem
                            key={album.id}
                            onClick={() => handleAlbumSelect(album)}
                            component="li"
                        > <ListItemAvatar>
                            <Avatar src={album.image} alt={album.name}/>
                        </ListItemAvatar>
                            <ListItemText primary={album.name}
                                          secondary={(<Box sx={{
                                              display: "flex",
                                              alignItems: "center"
                                          }}>
                                              {album.explicit ? <ExplicitIcon/> : <> </>}
                                              {album.album_type}
                                          </Box>)}/>
                        </ListItem>
                    ))}
                </List>
            )}
        </Box>
    );
};

export default AlbumSearch;
