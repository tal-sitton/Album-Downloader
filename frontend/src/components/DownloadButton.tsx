import React from 'react';
import {Button} from '@mui/material';
import {useDownloadAlbum} from '../api/api';

interface DownloadButtonProps {
    albumId: string | null;
    id3: boolean;
}

const DownloadButton: React.FC<DownloadButtonProps> = ({albumId, id3}) => {
    const mutation = useDownloadAlbum();

    return (
        <Button
            variant="contained"
            color="primary"
            disabled={!albumId}
            onClick={() =>
                albumId &&
                mutation.mutate({id: albumId, id3}, {
                    onSuccess: (_data) => {
                        alert(`Download started!`);
                    },
                    onError: () => {
                        alert('Error starting download');
                    },
                })
            }
            sx={{mt: 2}}
        >
            Download
        </Button>
    );
};

export default DownloadButton;
