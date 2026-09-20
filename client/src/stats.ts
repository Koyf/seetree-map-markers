import { SCORE_NAMES, SCORES, type Marker } from './types'

const panel = document.createElement('div')
panel.id = 'stats'
document.body.append(panel)

export function renderStats(markers: Marker[]): void {
  const rows = [`Total: ${markers.length}`]
  for (const score of [...SCORES].reverse()) {
    const count = markers.filter((m) => m.score === score).length
    rows.push(`${SCORE_NAMES[score]}: ${count}`)
  }
  panel.innerHTML = rows.map((r) => `<div>${r}</div>`).join('')
}
