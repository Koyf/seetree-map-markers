import { SCORE_COLORS, SCORES, type Score } from './types'

export function scoreButtons(selected: Score | null, onPick: (score: Score) => void): HTMLElement {
  const row = document.createElement('div')
  row.className = 'score-buttons'
  for (const score of SCORES) {
    const button = document.createElement('button')
    button.textContent = String(score)
    button.style.background = SCORE_COLORS[score]
    if (score === selected) button.classList.add('selected')
    button.addEventListener('click', () => onPick(score))
    row.append(button)
  }
  return row
}
