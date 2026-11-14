import { defineShikiSetup } from '@slidev/types'

// Code sits on a white card on the paper sheet: a light, high-contrast palette
// stays readable from the back of a room, where dark slides wash out on projectors.
export default defineShikiSetup(() => ({
  themes: {
    dark: 'github-light-high-contrast',
    light: 'github-light-high-contrast',
  },
}))
