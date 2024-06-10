import { ChangeEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import instance from "../../api/axiosConfig";
import PlusIcon from '../../assets/images/icon/ico-plus.svg'
import { useChannelInfoStore } from "../../store/channel";
import { MyChannelInfo } from "../../types/channel";
import { useUserInfoStore } from "../../store/user";

export default function Lobby() {
  const navigate = useNavigate();
  const setChannelInfo = useChannelInfoStore(state => state.setChannelInfo);
  const {user_name, user_nickname} = useUserInfoStore(state => ({
    user_name: state.user_name,
    user_nickname: state.user_nickname,
  }));

  const [channelCode, setChannelCode] = useState<string>("");
  const [myChannelList, setMyChannelList] = useState<MyChannelInfo[]>([]);

  const getEnterChannel = async () => {
    try {
      await instance.post("/channel/join", {
        params: { channel_code: channelCode },
      }).then(res => {
        console.log('res', res)
        // if(!res.data.channel) { 
        //   alert("채널이 존재하지 않습니다."); 
        //   setChannelCode("")
        // } else {
        //   setChannelInfo(res.data.channel);
        // }
      })
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  const getMyChannelList = async () => {
    try {
      await instance.get("/user/channel").then(res => {
        console.log('res', res)
        setMyChannelList(res.data)
        // if(!res.data.channel) { 
        //   alert("채널이 존재하지 않습니다."); 
        //   setChannelCode("")
        // }
      })
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  useEffect(() => {
    getMyChannelList();
  }, [])

  return (
    <div className="wrapper items-start justify-start">
      <div className="w-full flex justify-between items-center">
        <p className="text-[#3A4D39]"><em className="font-bold text-3xl">{user_name || user_nickname}</em> 님</p>
        <button className="w-8 rounded-full bg-button-3 hover:bg-button-2" type="button" onClick={() => navigate("/channel/create")}>
          <img src={PlusIcon} alt="채널 만들기" /> 채널 생성
        </button>
        {/* <p className="mt-2">채널 만들기</p> */}
      </div>

      <div className="w-full mt-8">
        <p>코드로 채널 가입하기</p>
        <div className="flex justify-between items-center gap-2 mt-2">
          <input 
            className="input flex-auto"
            type="text"
            value={channelCode}
            onChange={(event:ChangeEvent<HTMLInputElement>) => setChannelCode(event.target.value)}
            autoFocus
          />
          <button className="button flex-none" type="button" onClick={getEnterChannel} disabled={!channelCode}>가입</button>
        </div>
      </div>
      
      <div className="mt-8 w-full">
        <p className="title">내 채널 목록</p>
        {myChannelList?.map((item, idx)  => 
          <div key={idx} className="flex justify-between items-center gap-2">
            <span className="flex-auto">채널1</span>
            <button className="button flex-none" type="button" onClick={getEnterChannel}>채널 입장</button>
          </div>
        )}
      </div>
    </div>
  );
}
