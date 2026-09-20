import mapboxgl from 'mapbox-gl'

import { api } from './api'
import { map } from './map'
import { closePopup, isPopupOpen, openPopup } from './popup'
import { scoreButtons } from './scoreButtons'
import { renderStats } from './stats'
import { showError } from './toast'
import { SCORE_COLORS, type Marker, type Score } from './types'

const DRAG_THRESHOLD_PX = 3

interface Entry {
  data: Marker
  view: mapboxgl.Marker
  busy: boolean
}

const entries = new Map<string, Entry>()

// ---------- helpers ----------

function refreshStats(): void {
  renderStats([...entries.values()].map((e) => e.data))
}

function setColor(entry: Entry, score: Score): void {
  entry.view.getElement().style.setProperty('--color', SCORE_COLORS[score])
}

async function withMarkerLock(entry: Entry, action: () => Promise<void>): Promise<void> {
  const el = entry.view.getElement()
  entry.busy = true
  entry.view.setDraggable(false)
  el.classList.add('busy')
  try {
    await action()
  } catch (err) {
    showError(err)
  } finally {
    entry.busy = false
    entry.view.setDraggable(true)
    el.classList.remove('busy')
  }
}

// ---------- public API ----------

export function addMarker(data: Marker): void {
  const el = document.createElement('div')
  el.className = 'marker'
  const view = new mapboxgl.Marker({ element: el, draggable: true }).setLngLat(data).addTo(map)
  const entry: Entry = { data, view, busy: false }
  entries.set(data.id, entry)
  setColor(entry, data.score)
  bindMarkerEvents(entry)
  refreshStats()
}

function bindMarkerEvents(entry: Entry): void {
  const el = entry.view.getElement()
  let downAt = { x: 0, y: 0 }
  el.addEventListener('mousedown', (e) => {
    downAt = { x: e.clientX, y: e.clientY }
  })
  el.addEventListener('click', (e) => {
    e.stopPropagation()
    const moved = Math.hypot(e.clientX - downAt.x, e.clientY - downAt.y) > DRAG_THRESHOLD_PX
    if (!moved && !entry.busy) openEditPopup(entry)
  })
  entry.view.on('dragstart', closePopup)
  entry.view.on('dragend', () => void moveMarker(entry))
}

export function removeAllMarkers(): void {
  for (const entry of entries.values()) entry.view.remove()
  entries.clear()
  closePopup()
  refreshStats()
}

// ---------- edit / move / remove ----------

function openEditPopup(entry: Entry): void {
  const content = document.createElement('div')
  content.append(
    scoreButtons(entry.data.score, (score) => {
      closePopup()
      void changeScore(entry, score)
    }),
  )

  const remove = document.createElement('button')
  remove.className = 'remove-button'
  remove.textContent = 'Remove'
  remove.addEventListener('click', () => {
    closePopup()
    void removeMarker(entry)
  })
  content.append(remove)

  openPopup(entry.data, content)
}

function changeScore(entry: Entry, score: Score): Promise<void> {
  return withMarkerLock(entry, async () => {
    const { id, lng, lat } = entry.data
    entry.data = await api.replace(id, { lng, lat, score })
    setColor(entry, score)
    refreshStats()
  })
}

function moveMarker(entry: Entry): Promise<void> {
  return withMarkerLock(entry, async () => {
    const { id, score } = entry.data
    const { lng, lat } = entry.view.getLngLat()
    try {
      entry.data = await api.replace(id, { lng, lat, score })
    } catch (err) {
      entry.view.setLngLat(entry.data)
      throw err
    }
  })
}

function removeMarker(entry: Entry): Promise<void> {
  return withMarkerLock(entry, async () => {
    await api.remove(entry.data.id)
    entry.view.remove()
    entries.delete(entry.data.id)
    refreshStats()
  })
}

// ---------- create ----------

async function createMarker(lngLat: mapboxgl.LngLat, score: Score): Promise<void> {
  try {
    addMarker(await api.create({ lng: lngLat.lng, lat: lngLat.lat, score }))
  } catch (err) {
    showError(err)
  }
}

export function enableMarkerCreation(): void {
  map.on('click', (e) => {
    if (isPopupOpen()) {
      closePopup()
      return
    }
    openPopup(
      e.lngLat,
      scoreButtons(null, (score) => {
        closePopup()
        void createMarker(e.lngLat, score)
      }),
    )
  })
  refreshStats()
}
