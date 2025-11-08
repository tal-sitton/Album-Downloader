import axios from 'axios';
import {useMutation, useQuery, useQueryClient} from '@tanstack/react-query';
import {useEffect, useState} from "react";

// Types
export interface Artist {
    name: string;
    id: string;
    image?: string;
}

export interface Album {
    name: string;
    artist: Artist;
    release_date_epoch: number;
    image: string;
    url: string;
    id: string;
    album_type: string;
    explicit: boolean;
}

export interface DownloadStatus {
    uid: string;
    artist: string;
    album: string;
    thumbnail: string;
    status: string;
    info: string;
    id3: boolean;
}

// Axios Instance
const api = axios.create({
    baseURL: '/api',
});

// API Functions
export const useArlsCount = () =>
    useQuery({queryKey: ["arls_count"], queryFn: fetchArlsCount});

export const fetchArlsCount = async (): Promise<number> => {
    const {data} = await api.get<number>(`/arl/count`);
    return data;
};

export const useRenewArls = (enabled: boolean) =>
    useQuery({queryKey: ["renew_arls"], queryFn: fetchRenewArls, enabled});

export const fetchRenewArls = async (): Promise<string> => {
    const {data} = await api.get<string>(`/arl/new`);
    return data;
};

export const useNewArl = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (new_arl: string) => postNewArl(new_arl),
        onSuccess: () => {
            queryClient.invalidateQueries({queryKey: ["arls_count"]});
        },
    });
};

export const postNewArl = async (new_arl: string): Promise<void> => {
    await api.post<void>(`/arl/renew`, {arl: new_arl});
};


export const fetchArtists = async (name: string): Promise<Artist[]> => {
    const {data} = await api.get<Artist[]>('/artists', {params: {name}});
    return data;
};

export const useFetchArtists = (name: string) =>
    useQuery({
        queryKey: ['artists', name],
        queryFn: () => fetchArtists(name),
        enabled: name.trim().length > 0,
    });


export const fetchAlbums = async (artistId: string): Promise<Album[]> => {
    const {data} = await api.get<Album[]>('/albums', {params: {artist_id: artistId}});
    return data;
};

export const useFetchAlbums = (artistId: string) =>
    useQuery({
        queryKey: ['albums', artistId],
        queryFn: () => fetchAlbums(artistId),
        enabled: !!artistId
    });

export const downloadAlbum = async (id: string, id3: boolean): Promise<string> => {
    const {data} = await api.post<string>(`/download_album/${id}?id3=${id3}`);
    return data;
};


export const useDownloadAlbum = () =>
    useMutation({mutationFn: ({id, id3}: { id: string; id3: boolean }) => downloadAlbum(id, id3)});

export const fetAlbumsStatus = async (): Promise<DownloadStatus[]> => {
    const {data} = await api.get<DownloadStatus[]>(`/album_status`);
    return data;
};

export const useFetchAlbumsStatus = () =>
    useQuery({queryKey: ['albums_status'], queryFn: fetAlbumsStatus, refetchInterval: 2 * 1000});

export const zipAlbums = async (uids: string[]): Promise<string> => {
    const {data} = await api.get<string>('/zip_downloaded_albums', {
        params: {uids}, paramsSerializer: (params: any) => {
            return new URLSearchParams(params).toString();
        }
    });
    return data;
}

export const getZipRoute = (zipName: string) => api.defaults.baseURL + `/output/${zipName}`;


export const useWebSocketAlbumsStatus = () => {
    const [albumsStatus, setAlbumsStatus] = useState<DownloadStatus[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // const ws = new WebSocket('/api/album_statuses/');
        const ws = new WebSocket('/api/albums_status');

        ws.onopen = () => {
            console.log('Connected to websocket');
            setIsLoading(false);
        };

        ws.onmessage = (event) => {
            const data: DownloadStatus[] = JSON.parse(event.data);
            setAlbumsStatus(data);
        };

        ws.onclose = () => {
            console.log('Disconnected from websocket');
            setIsLoading(true);
        };

        return () => {
            ws.close();
        };
    }, []);

    return {albumsStatus, isConnected: isLoading};
};