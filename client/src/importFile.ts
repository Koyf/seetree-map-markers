import { api } from './api'
import { addMarker } from './markers'
import { showError, showInfo } from './toast'
import type { MarkerIn } from './types'

function parseImportFile(text: string): MarkerIn[] {
  const parsed: unknown = JSON.parse(text)
  const markers = (parsed as { markers?: unknown })?.markers
  if (!Array.isArray(markers)) throw new Error('Expected {"markers": [...]}')
  return markers.map((item: unknown) => {
    if (typeof item !== 'object' || item === null) {
      throw new Error('Every marker must be an object with lng, lat, score')
    }
    const { lng, lat, score } = item as MarkerIn
    return { lng, lat, score }
  })
}

async function importFile(file: File): Promise<void> {
  try {
    const imported = await api.importMany(parseImportFile(await file.text()))
    if (imported.length === 0) {
      showInfo('The file contains no markers')
      return
    }
    imported.forEach(addMarker)
  } catch (err) {
    showError(`Import failed: ${err instanceof Error ? err.message : String(err)}`)
  }
}

const fileInput = document.createElement('input')
fileInput.type = 'file'
fileInput.accept = '.json,application/json'
fileInput.hidden = true
fileInput.addEventListener('change', () => {
  const file = fileInput.files?.[0]
  if (file) void importFile(file)
  fileInput.value = ''
})
document.body.append(fileInput)

export function pickAndImport(): void {
  fileInput.click()
}
