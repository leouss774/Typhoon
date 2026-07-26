import { defineConfig } from 'vite';

export default defineConfig({
  envDir: '..',
  server: {
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/osm-tiles': { target: 'https://tile.openstreetmap.org', changeOrigin: true, rewrite: (p) => p.replace(/^\/osm-tiles/, '') },
      '/georisques-wms': { target: 'https://www.georisques.gouv.fr', changeOrigin: true, rewrite: (p) => p.replace(/^\/georisques-wms/, '/services') },
      '/bdnb-tiles': { target: 'https://api.bdnb.io', changeOrigin: true, rewrite: (p) => p.replace(/^\/bdnb-tiles/, '/v1/bdnb/tuiles') },
      '/ign-geocodage': { target: 'https://data.geopf.fr', changeOrigin: true, rewrite: (p) => p.replace(/^\/ign-geocodage/, '/geocodage') },
      '/ban-api': { target: 'https://api-adresse.data.gouv.fr', changeOrigin: true, rewrite: (p) => p.replace(/^\/ban-api/, '') },
      '/georisques-api': { target: 'https://www.georisques.gouv.fr', changeOrigin: true, rewrite: (p) => p.replace(/^\/georisques-api/, '/api/v1') },
      '/georisques-v2-api': { target: 'https://www.georisques.gouv.fr', changeOrigin: true, rewrite: (p) => p.replace(/^\/georisques-v2-api/, '/api/v2') },
      '/bdnb-api': { target: 'https://api.bdnb.io', changeOrigin: true, rewrite: (p) => p.replace(/^\/bdnb-api/, '/v1/bdnb') },
    },
  },
});
