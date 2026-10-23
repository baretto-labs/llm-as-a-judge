import { defineShikiSetup } from '@slidev/types'

// Code always sits on the slate board, so both schemes use a dark palette.
export default defineShikiSetup(() => ({
  themes: {
    dark: 'vitesse-dark',
    light: 'vitesse-dark',
  },
}))
