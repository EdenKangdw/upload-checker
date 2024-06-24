import { ChangeEvent, useEffect, useState } from "react"
import { useNavigate, useLocation } from "react-router-dom";
import instance from "../../api/axiosConfig";
import { useUserInfoStore } from "../../store/user";
import { GroupList } from "../../types/channel";

export default function GetUserInfo () {
  const navigate = useNavigate();
  const location = useLocation();
  const { data: channelId }= location.state || {};
  const setUserInfo = useUserInfoStore(state => state.setUserInfo);

  const [nickname, setNickName] = useState<string>("");
  const [groupId, setGroupId] = useState<number>(0);
  const [optionList, setOptionList] = useState<GroupList[]>([]);

  const getEnterChannel = async () => {
    try {
      await instance.get(`/channel?channel_id=${channelId}`).then(res => {
        navigate('/channel', { state: { data: res.data} });
      })
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  const postUserInfo = async () => {
    try {
      await instance.post("/user", {
        nickname: nickname,
        group_id: groupId,
      }).then(res => {
        setUserInfo(res.data);
        getEnterChannel();
      })
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  const getTeamList = async () => {
    try {
      await instance.get("/group/list").then(res => {
        setOptionList(res.data);
        setGroupId(res.data[0].group_id);
      })
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  useEffect(() => {
    getTeamList();
  }, []);

  return (
    <div className="wrapper items-center justify-center text-center">
      <label>이름(실명)을 입력해 주세요.(필수)
        <input className="input block mt-2 mx-auto" autoFocus value={nickname} onChange={(event: ChangeEvent<HTMLInputElement>) => setNickName(event.target.value)} />
      </label>
      <label className="block mt-6">소속 되어있는 팀을 선택해 주세요.(필수)
        <select name="cars" className="block mt-2 mx-auto py-1 px-2 rounded-md outline-none" onChange={(e: ChangeEvent<HTMLSelectElement>) => setGroupId(Number(e.target.value))}>
          {optionList.map(item => 
            <option key={item.group_id} value={item.group_id}>{item.group_name}</option>
          )};
        </select>
      </label>
      <button 
        className="button mt-8" 
        type="submit" 
        onClick={postUserInfo} 
        disabled={!Boolean(groupId && nickname)}
      >
        저장
      </button>
    </div>
  );
};