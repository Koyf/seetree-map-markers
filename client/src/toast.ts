const TOAST_MS = 4000

const container = document.createElement('div')
container.id = 'toasts'
document.body.append(container)

function show(message: unknown, kind: 'error' | 'info'): void {
  const el = document.createElement('div')
  el.className = `toast toast-${kind}`
  el.textContent = message instanceof Error ? message.message : String(message)
  container.append(el)
  setTimeout(() => el.remove(), TOAST_MS)
}

export function showError(error: unknown): void {
  show(error, 'error')
}

export function showInfo(message: string): void {
  show(message, 'info')
}
