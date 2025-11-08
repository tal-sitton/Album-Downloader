import React from 'react';
import {QueryClient, QueryClientProvider} from '@tanstack/react-query';
import {Box, createTheme, Tab, Tabs, ThemeProvider} from '@mui/material';
import SearchToDownload from "./components/SearchToDownload";
import {TabContext, TabPanel} from "@mui/lab";
import Downloads from "./components/Downloads";
import ArlsStatus from "./components/ArlsStatus";

const queryClient = new QueryClient();

const theme = createTheme({
    palette: {
        primary: {
            main: '#cf8c7c', // Rich red
            contrastText: '#FFFFFF', // White for text contrast
        },
        secondary: {
            main: '#FF9800', // Bright orange
            contrastText: '#000000', // Black for text contrast
        },
        error: {
            main: '#f60000', // Crimson
        },
        warning: {
            main: '#FFB300', // Golden yellow
        },
        info: {
            main: '#7B1FA2', // Deep purple
        },
        success: {
            main: '#388E3C', // Forest green
        },
        background: {
            default: '#F3E5F5', // Light purple hue
            paper: '#FFFFFF', // White for paper components
        },
        text: {
            primary: '#cf8c7c', // Chocolate brown for primary text
            secondary: '#6D4C41', // Mocha for secondary text
        },
    },
    components: {
        MuiOutlinedInput: {
            styleOverrides: {
                root: {
                    '& fieldset': {
                        borderColor: '#6D4C41', // Default color
                    },
                    '&:hover fieldset': {
                        borderColor: '#FF9800', // Hover color
                    },
                    '&.Mui-focused fieldset': {
                        borderColor: '#cf8c7c', // Focused color
                    },
                },
            },
        },
    }
});


const App: React.FC = () => {
    const [currentTab, setCurrentTab] = React.useState(0);

    return (
        <ThemeProvider theme={theme}>
            <QueryClientProvider client={queryClient}>
                <Box
                    sx={{
                        display: 'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        alignItems: 'center',
                        textAlign: 'center',
                        width: '100vw'
                    }}
                >
                    <TabContext value={currentTab}>
                        <Tabs value={currentTab} onChange={(e, v) => setCurrentTab(v)}>
                            <Tab label="Search To Download"/>
                            <Tab label="Downloads Status"/>
                        </Tabs>
                        <TabPanel value={0}>
                            <SearchToDownload/>
                        </TabPanel>
                        <TabPanel value={1}>
                            <Downloads/>
                        </TabPanel>
                    </TabContext>
                    <ArlsStatus/>
                </Box>
            </QueryClientProvider>
        </ThemeProvider>
    );
};

export default App;
