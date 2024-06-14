import { ChangeEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import instance from "../../api/axiosConfig";
import { ChannelListItem } from "../../types/channel";

export default function Lobby() {
  const navigate = useNavigate();

  const [channelCode, setChannelCode] = useState<string>("");
  const [myChannelList, setMyChannelList] = useState<ChannelListItem[]>([]);
  const [myName, setMyName] = useState<{username:string; nickname:string}>({
    username: "",
    nickname: "",
  });

  const postJoinChannel = async () => {
    try {
      await instance.post("/channel/join", {
        channel_code: channelCode,
      }).then(res => {
        console.log('res', res)
        getMyChannelList();
        setChannelCode("");
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

  const getEnterChannel = async (channelId: number) => {
    try {
      await instance.get(`/channel?channel_id=${channelId}`).then(res => {
        // setChannelInfo(res.data);
        navigate('/channel', { state: { data: res.data} });
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

  const getUserInfo = async () => {
    try {
      await instance.get("/user").then(res => {
        setMyName({
          username: res.data.user_name,
          nickname: res.data.user_nickname,
        });
      });
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  useEffect(() => {
    getUserInfo();
    getMyChannelList();
  }, [])

  return (
    <div className="wrapper items-start justify-start">
      <div className="w-full flex justify-between items-center">
        <p className="text-[#3A4D39]"><em className="font-bold text-3xl">{myName.nickname || myName.username}</em> 님</p>
        <button className="button1 before:content-plusIcon before:inline-block before:w-6 before:align-middle" type="button" onClick={() => navigate("/channel/create")}>
          채널 생성
        </button>
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
          <button className="button flex-none" type="button" onClick={postJoinChannel} disabled={!channelCode}>가입</button>
        </div>
      </div>
      
      {myChannelList.length > 0 && 
        <div className="mt-8 w-full">
          <p className="title">내 채널 목록</p>
          {myChannelList?.map((item) => 
            <div key={item.channel_id} className="flex justify-between items-center gap-2">
              <span className="flex-auto">{item.channel_name}</span>
              <button className="button flex-none" type="button" onClick={() => getEnterChannel(item.channel_id)}>채널 입장</button>
            </div>
          )}
        </div>
      }
    </div>
  );
}
