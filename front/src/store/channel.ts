import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { ChannelInfo } from '../types/channel';
 
interface Actions  {
  setChannelInfo: (payload: ChannelInfo) => void
}

const initialState: ChannelInfo = {  
  channel_check_type: "check",
  channel_code: "",
  channel_creator_id: 0,
  channel_id: 0,
  channel_name: "",
  channel_user_count:  0,
  created_at: "",
  updated_at: "", 
}

export const useChannelInfoStore = create<ChannelInfo & Actions>()(
  persist(
    (set) => ({
      ...initialState,
      setChannelInfo: (payload: ChannelInfo) => set((state) => ({  
        channel_check_type: state.channel_check_type = payload.channel_check_type,
        channel_code: state.channel_code = payload.channel_code,
        channel_creator_id: state.channel_creator_id = payload.channel_creator_id,
        channel_id: state.channel_id = payload.channel_id,
        channel_name: state.channel_name = payload.channel_name,
        channel_user_count: state.channel_user_count = payload.channel_user_count,
        created_at: state.created_at = payload.created_at,
        updated_at: state.updated_at = payload.updated_at, 
      })),
    }),
    {
      name: 'channel-info', // name of item in the storage (must be unique)
      // storage: createJSONStorage(() => sessionStorage), // (optional) by default the 'localStorage' is used
      // partialize: (state) => ({ bears: state.bears }),
    },
  ),
);