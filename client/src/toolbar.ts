import { EXPORT_URL } from './api'

interface ToolbarActions {
  onImport: () => void
  onClear: () => void
}

export function buildToolbar({ onImport, onClear }: ToolbarActions): void {
  const toolbar = document.createElement('div')
  toolbar.id = 'toolbar'

  const exportLink = document.createElement('a')
  exportLink.className = 'toolbar-button'
  exportLink.href = EXPORT_URL
  exportLink.textContent = 'Export'

  toolbar.append(exportLink, button('Import', onImport), button('Clear all', onClear))
  document.body.append(toolbar)
}

function button(label: string, onClick: () => void): HTMLButtonElement {
  const el = document.createElement('button')
  el.className = 'toolbar-button'
  el.textContent = label
  el.addEventListener('click', onClick)
  return el
}
