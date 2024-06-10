import { create } from 'zustand'
import { persist, createJSONStorage } from 'zustand/middleware'

interface State  {
  token: string
}

interface Actions  {
  setToken: (payload: string) => void
}

const initialState:State = {
  token:""
}

export const useAuthStore = create<State & Actions>()(
  persist(
    (set) => ({
      ...initialState,
      setToken: (payload: string) => set((state) => ({ token: state.token = payload })),
    }),
    {
      name: 'access-token', // name of item in the storage (must be unique)
      // storage: createJSONStorage(() => sessionStorage), // (optional) by default the 'localStorage' is used
      // partialize: (state) => ({ bears: state.bears }),
    },
  ),
)