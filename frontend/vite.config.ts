import {defineConfig} from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
    plugins: [react()],
    server: {
        proxy: {
            "/api/albums_status": {
                target: "ws://localhost:80",
                changeOrigin: true,
                ws: true,
            },
            "/api": {
                target: "http://localhost:80",
                changeOrigin: true,
                secure: false,
            },
        },
    }
})
