import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { UserInfo } from '../types/channel';

interface Actions  {
  setUserInfo: (payload: UserInfo) => void
}

const initialState: UserInfo = {  
  user_id: 0,
  user_name: "", 
  user_nickname: null,
  updated_at: "",
  created_at: "",
}

export const useUserInfoStore = create<UserInfo & Actions>()(
  persist(
    (set) => ({
      ...initialState,
      setUserInfo: (payload: UserInfo) => set((state) => ({  
        user_id: state.user_id = payload.user_id,
        user_name: state.user_name = payload.user_name,
        user_nickname: state.user_nickname = payload.user_nickname, 
        updated_at: state.updated_at = payload.updated_at, 
        created_at: state.created_at = payload.created_at, 
      })),
    }),
    {
      name: 'user-info', // name of item in the storage (must be unique)
      // storage: createJSONStorage(() => sessionStorage), // (optional) by default the 'localStorage' is used
      // partialize: (state) => ({ bears: state.bears }),
    },
  ),
);