import { create } from 'zustand'

let _id = 0

const useToastStore = create((set) => ({
  toasts: [],

  addToast: (message, type = 'info', duration = 4000) => {
    const id = ++_id
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }))
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }))
    }, duration)
  },

  removeToast: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))

// Convenience helpers usable outside React
export const toast = {
  success: (msg, d) => useToastStore.getState().addToast(msg, 'success', d),
  error: (msg, d) => useToastStore.getState().addToast(msg, 'error', d),
  info: (msg, d) => useToastStore.getState().addToast(msg, 'info', d),
  warning: (msg, d) => useToastStore.getState().addToast(msg, 'warning', d),
}

export default useToastStore
