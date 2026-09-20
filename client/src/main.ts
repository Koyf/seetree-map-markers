import './style.css'

import { api } from './api'
import { pickAndImport } from './importFile'
import { addMarker, enableMarkerCreation, removeAllMarkers } from './markers'
import { showError } from './toast'
import { buildToolbar } from './toolbar'

async function loadMarkers(): Promise<void> {
  try {
    const markers = await api.list()
    markers.forEach(addMarker)
  } catch (err) {
    showError(err)
  }
}

async function clearMarkers(): Promise<void> {
  try {
    await api.clear()
    removeAllMarkers()
  } catch (err) {
    showError(err)
  }
}

buildToolbar({ onImport: pickAndImport, onClear: () => void clearMarkers() })
enableMarkerCreation()
void loadMarkers()
