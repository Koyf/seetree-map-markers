export type Score = 0 | 1 | 2 | 3 | 4 | 5

export interface Marker {
  id: string
  lng: number
  lat: number
  score: Score
}

export type MarkerIn = Omit<Marker, 'id'>

export const SCORES: readonly Score[] = [0, 1, 2, 3, 4, 5]

export const SCORE_COLORS: Record<Score, string> = {
  0: '#000000', // black
  1: '#808080', // gray
  2: '#ff0000', // red
  3: '#ffa500', // orange
  4: '#00ff00', // lime
  5: '#008000', // green
}

export const SCORE_NAMES: Record<Score, string> = {
  0: 'Zero',
  1: 'One',
  2: 'Two',
  3: 'Three',
  4: 'Four',
  5: 'Five',
}
