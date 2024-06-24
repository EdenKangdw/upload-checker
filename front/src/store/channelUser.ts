import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import {  UserInfoForChannel } from '../types/channel';

interface Actions  {
  setChannelUserInfo: (payload: UserInfoForChannel) => void
}

const initialState: UserInfoForChannel = {  
  user_id: 0,
  channel_id: 0, 
  isCreator: false,
  isManager: false,
  user_nickname: "",
  group: {
    id: 0,
    name: "",
    type: "MEMBER",
  }
};

export const useChannelUserInfoStore = create<UserInfoForChannel & Actions>()(
  persist(
    (set) => ({
      ...initialState,
      setChannelUserInfo: (payload: UserInfoForChannel) => set((state) => ({  
        user_id: state.user_id = payload.user_id,
        user_nickname: state.user_nickname = payload.user_nickname,
        channel_id: state.channel_id = payload.channel_id,
        isCreator: state.isCreator = payload.isCreator, 
        isManager: state.isManager = payload.isManager, 
        group: state.group = payload.group, 
      })),
    }),
    {
      name: 'channel-user-info', // name of item in the storage (must be unique)
      // storage: createJSONStorage(() => sessionStorage), // (optional) by default the 'localStorage' is used
      // partialize: (state) => ({ bears: state.bears }),
    },
  ),
);