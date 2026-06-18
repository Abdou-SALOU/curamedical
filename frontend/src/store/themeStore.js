import { create } from 'zustand'
import { persist } from 'zustand/middleware'

const getSystemTheme = () =>
  typeof window !== 'undefined' && window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark' : 'light'

const applyTheme = (resolved) => {
  const html = document.documentElement
  html.setAttribute('data-theme', resolved)
  if (resolved === 'dark') html.classList.add('dark')
  else html.classList.remove('dark')
}

const useThemeStore = create(
  persist(
    (set, get) => ({
      // 'light' | 'dark' | 'system'
      theme: 'system',
      resolvedTheme: 'light',

      init() {
        const { theme } = get()
        const resolved = theme === 'system' ? getSystemTheme() : theme
        applyTheme(resolved)
        set({ resolvedTheme: resolved })

        // Listen for system changes when set to 'system'
        const mq = window.matchMedia('(prefers-color-scheme: dark)')
        const handler = (e) => {
          if (get().theme === 'system') {
            const r = e.matches ? 'dark' : 'light'
            applyTheme(r)
            set({ resolvedTheme: r })
          }
        }
        mq.addEventListener('change', handler)
      },

      toggle() {
        const { resolvedTheme } = get()
        const next = resolvedTheme === 'dark' ? 'light' : 'dark'
        applyTheme(next)
        set({ theme: next, resolvedTheme: next })
      },

      setTheme(theme) {
        const resolved = theme === 'system' ? getSystemTheme() : theme
        applyTheme(resolved)
        set({ theme, resolvedTheme: resolved })
      },
    }),
    { name: 'cura-theme', partialize: (s) => ({ theme: s.theme }) }
  )
)

export default useThemeStore
