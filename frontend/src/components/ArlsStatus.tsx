import React, {useState} from 'react';
import {Alert, Button, CircularProgress, TextField, Tooltip, Typography} from '@mui/material';
import {useArlsCount, useNewArl, useRenewArls} from "../api/api";
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';

const ArlsStatus: React.FC = () => {
    const {data: arls_count, isLoading} = useArlsCount();
    const {refetch: renewArls, data: arl_url, isFetching: isLoadingArls} = useRenewArls(false);
    const [isRenewed, setIsRenewed] = useState(false);
    const {mutate: addArl, isPending: isLoadingNewArl} = useNewArl();


    return (
        isLoadingNewArl || isLoading ? <CircularProgress/> :
            <Alert variant="filled" severity={arls_count! == 0 ? "error" : arls_count! < 3 ? "warning" : "success"}
                   sx={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}
                   action={arls_count! >= 3 ? <></> : isLoadingArls ? <CircularProgress/> :
                       !isRenewed ? (<Button
                           size="small"
                           variant="outlined"
                           color="inherit"
                           onClick={async () => {
                               await renewArls()
                               setIsRenewed(true);
                           }
                           }
                           sx={{verticalAlign: 0, padding: 0, margin: 0}}
                       >
                           Renew
                       </Button>) : undefined}
            >
                There are {arls_count} ARLs online
                {isRenewed ?
                    <>
                        <br/>
                        <Button sx={{color: "blue"}} href={arl_url!} target={"_blank"}>Verify account</Button>
                        <br/>
                        <div style={{display: "flex", alignItems: "center", gap: "8px"}}>
                        <TextField label={"ARL"} size={"small"} variant={"filled"}
                                   sx={{input: {color: "black"}}}
                                   onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                                       if (event.target.value.length === 192) {
                                           addArl(event.target.value);
                                           setIsRenewed(false);
                                       }
                                   }}></TextField>
                        <Tooltip title={
                            <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
                            <Typography color="inherit" fontWeight={"medium"}>Paste the ARL</Typography>
                            {'Click "VERIFY ACCOUNT" → F12 → Application → Cookies → "https://www.deezer.com/" → the cookie named "arl"\''}
                            </div>}>
                                <HelpOutlineIcon />
                        </Tooltip>
                        </div>
                    </> : <></>}
                <></>
            </Alert>
    );
};

export default ArlsStatus;
