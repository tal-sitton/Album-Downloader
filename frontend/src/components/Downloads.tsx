import React, {useState} from "react";
import {getZipRoute, useFetchAlbumsStatus, useWebSocketAlbumsStatus, zipAlbums} from "../api/api";
import {
    Accordion,
    AccordionDetails,
    AccordionSummary,
    Alert,
    Button,
    Card,
    CardActions,
    CardContent,
    CardMedia,
    Checkbox,
    CircularProgress,
    FormControlLabel,
    Grid2,
    Snackbar,
    Switch,
    Tooltip,
    Typography,
} from "@mui/material";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';

interface SnackbarState {
    open: boolean;
    message: string;
    severity: "success" | "error" | "warning" | "info";
}

const Downloads: React.FC = () => {
    const [selectedAlbums, setSelectedAlbums] = useState<string[]>([]);
    const [zipping, setZipping] = useState<boolean>(false);
    const [snackbar, setSnackbar] = useState<SnackbarState>({
        open: false,
        message: "",
        severity: "success",
    });
    // const {data: albums, isLoading} = useFetchAlbumsStatus();
    const { albumsStatus: albums, isConnected: isLoading } = useWebSocketAlbumsStatus();    const [showErrors, setShowErrors] = useState<boolean>(false);

    const handleCheckboxChange = (uid: string) => {
        setSelectedAlbums((prev) =>
            prev.includes(uid) ? prev.filter((id) => id !== uid) : [...prev, uid]
        );
    };

    const handleZipAlbums = async () => {
        if (selectedAlbums.length === 0) {
            setSnackbar({open: true, message: "No albums selected", severity: "warning"});
            return;
        }

        try {
            setZipping(true);
            const zipName = await zipAlbums(selectedAlbums);
            const zipRoute = getZipRoute(zipName);
            const newWindow = window.open();
            if (!newWindow) {
                throw new Error("Failed to open new window to download");
            }
            newWindow.location = zipRoute;
            setTimeout(function () {
                newWindow.close();
            }, 50);
            setSnackbar({open: true, message: "Albums zipped successfully!", severity: "success"});
        } catch (error) {
            console.error("Failed to zip albums:", error);
            setSnackbar({open: true, message: "Failed to zip albums", severity: "error"});
        } finally {
            setZipping(false);
        }
    };

    if (isLoading) {
        return <CircularProgress/>;
    }

    return <>
        <FormControlLabel control={<Switch value={showErrors} onChange={(_, checked) => setShowErrors(checked)}/>}
                          label="Show Errors"/>

        <Grid2 container spacing={2} justifyContent={'center'} width={"90vw"}>
            {albums?.map((album) => (
                (showErrors || album.status !== "error") &&
                <Grid2 key={album.uid} size={{xs: 10, md: 2}}>
                    <Card>
                        {album.thumbnail ? <CardMedia
                            component="img"
                            height="140"
                            image={album.thumbnail}
                            alt={`${album.album} cover`}
                        /> : <CircularProgress/>}
                        <CardContent>
                            <Tooltip title={album.album}>
                                <Typography
                                    variant="h6"
                                    sx={{
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                    }}
                                >
                                    {album.album}
                                </Typography>
                            </Tooltip>
                            <Tooltip title={album.artist}>
                                <Typography
                                    variant="subtitle1"
                                    sx={{
                                        whiteSpace: "nowrap",
                                        overflow: "hidden",
                                        textOverflow: "ellipsis",
                                    }}
                                >
                                    {album.artist}
                                </Typography>
                            </Tooltip>
                            <Typography variant="body2"
                                        color={album.status === "error" ? "error.main" : album.status === "downloaded" ? "success.main" : "text.main"}>
                                Status: {album.status}
                            </Typography>
                            {album.status !== "error" &&
                                <Typography variant="body2">{album.info.split('*')[0]}</Typography>}
                            {(album.status === "error" || album.info.includes("*")) && (
                                <Accordion>
                                    <AccordionSummary
                                        expandIcon={<ExpandMoreIcon/>}
                                    >
                                        More Info
                                    </AccordionSummary>
                                    <AccordionDetails>
                                        {album.status === 'error' ? album.info : album.info.split('*')[1].split("\n").map((value) => <>{value}<br/></>)}
                                    </AccordionDetails>
                                </Accordion>
                            )}
                        </CardContent>
                        {album.id3 && <Typography variant="body2" color="error">ID3</Typography>}
                        {album.status === "downloaded" && (
                            <CardActions>
                                <Checkbox
                                    checked={selectedAlbums.includes(album.uid)}
                                    onChange={() => handleCheckboxChange(album.uid)}
                                />
                                <Typography>Select</Typography>
                            </CardActions>
                        )}
                    </Card>
                </Grid2>
            ))}
        </Grid2>
        {zipping ? <CircularProgress/> :
            <Button
                variant="contained"
                color="primary"
                onClick={handleZipAlbums}
                disabled={zipping || selectedAlbums.length === 0}
                style={{marginTop: "16px"}}
            >
                Download Selected Albums
            </Button>
        }
        <Snackbar
            open={snackbar.open}
            autoHideDuration={2000}
            onClose={() => setSnackbar({...snackbar, open: false})}
        >
            <Alert
                onClose={() => setSnackbar({...snackbar, open: false})}
                severity={snackbar.severity}
            >
                {snackbar.message}
            </Alert>
        </Snackbar>
    </>
}

export default Downloads;
