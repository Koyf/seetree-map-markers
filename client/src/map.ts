import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'

import { showError } from './toast'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN
if (!mapboxgl.accessToken) {
  showError('VITE_MAPBOX_TOKEN is not set. Copy .env.example to .env and add the token.')
}

export const map = new mapboxgl.Map({
  container: 'map',
  style: 'mapbox://styles/mapbox/streets-v12',
  center: [34.78, 32.07],
  zoom: 10,
})
