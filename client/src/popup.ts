import mapboxgl from 'mapbox-gl'

import { map } from './map'

let popup: mapboxgl.Popup | null = null

export function isPopupOpen(): boolean {
  return popup !== null
}

export function closePopup(): void {
  popup?.remove()
  popup = null
}

export function openPopup(lngLat: mapboxgl.LngLatLike, content: HTMLElement): void {
  closePopup()
  popup = new mapboxgl.Popup({ closeButton: false, closeOnClick: false, offset: 12 })
    .setLngLat(lngLat)
    .setDOMContent(content)
    .addTo(map)
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closePopup()
})
