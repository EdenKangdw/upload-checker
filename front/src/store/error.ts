import { create } from 'zustand'

interface State  {
  errorMsg: string
}

interface Actions  {
  setErrorMsg: (payload: string) => void
}

const initialState:State = {
  errorMsg:""
}

export const useErrorMagStore = create<State & Actions>(
  (set) => ({
    ...initialState,
    setErrorMsg: (payload: string) => set((state) => ({ errorMsg: state.errorMsg = payload })),
  }),
)