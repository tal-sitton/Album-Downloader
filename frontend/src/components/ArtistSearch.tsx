import React, {useCallback, useState} from 'react';
import {debounce} from 'lodash';
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
import {Artist, useFetchArtists} from '../api/api';

interface ArtistSearchProps {
    onSelectArtist: (artistId: string | null) => void;
}

const ArtistSearch: React.FC<ArtistSearchProps> = ({onSelectArtist}) => {
    const [search, setSearch] = useState<string>('');
    const [searchString, setSearchString] = useState<string>('');
    const [selectedArtist, setSelectedArtist] = useState<Artist | null>(null);
    const {data: artists, isLoading} = useFetchArtists(search);


    const fetchDebounce = useCallback(
        debounce((value: string) => {
            setSearch(value);
        }, 500),
        []
    );

    const handleInputChange = (value: string) => {
        setSearchString(value);
        setSelectedArtist(null);
        onSelectArtist(null);
        fetchDebounce(value);
    }

    const handleArtistSelect = (artist: Artist) => {
        setSelectedArtist(artist);
        onSelectArtist(artist.id);
    };

    return (
        <Box sx={{width: '100%', maxWidth: 600, mx: 'auto', mb: 4}}>
            <TextField
                label="Search Artist"
                variant="outlined"
                fullWidth
                onChange={(e) => handleInputChange(e.target.value)}
                value={selectedArtist ? selectedArtist.name : searchString}
                slotProps={{
                    input: {
                        startAdornment: selectedArtist && (
                            <InputAdornment position="start">
                                <Avatar src={selectedArtist.image} alt={selectedArtist.name}
                                        sx={{width: 32, height: 32}}/>
                            </InputAdornment>
                        ),
                    }
                }}
                sx={{mb: 2}}
            />
            {isLoading && <CircularProgress/>}
            {!selectedArtist && (
                <List>
                    {artists?.map((artist: Artist) => (
                        <ListItem key={artist.id} onClick={() => handleArtistSelect(artist)}>
                            <ListItemAvatar>
                                <Avatar src={artist.image} alt={artist.name}/>
                            </ListItemAvatar>
                            <ListItemText primary={artist.name}/>
                        </ListItem>
                    ))}
                </List>
            )}
        </Box>
    );
};

export default ArtistSearch;
