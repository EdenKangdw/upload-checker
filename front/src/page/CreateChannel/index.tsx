import  { ChangeEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import instance from "../../api/axiosConfig";
import { useChannelInfoStore } from "../../store/channel";
import HomeIcon from  '../../assets/images/icon/ico-home.svg'
import { useErrorMagStore } from "../../store/error";
import Error from "../../component/Error";

function CreateChannel() {
  const navigate = useNavigate();
  const setChannelInfo = useChannelInfoStore(state => state.setChannelInfo);
  const {errorMsg, setErrorMsg} = useErrorMagStore(state => ({
    errorMsg : state.errorMsg,
    setErrorMsg : state.setErrorMsg,
  }));

  const [channelName, setChannelName] = useState<string>("");
  const [channelCode, setChannelCode] = useState<string>("");

  const fetchPostCreateChannel = async () => {
    try {
      await instance.post("/channel", {
          name: channelName,
          code: channelCode,
          check_type: "check",
        },
      ).then(res => {
        setErrorMsg("");
        setChannelInfo(res.data);
        alert("채널이 생성되었습니다.")
        navigate("/lobby");
      })
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  useEffect(() => {
    errorMsg && setChannelCode("")
  }, [errorMsg])

  return (
    <div className="wrapper items-center justify-center text-center">
      <button className="w-8" type="button" onClick={()=>navigate("/lobby")}>
        <img src={HomeIcon} alt="홈으로 가기" />
      </button>
      <label className="block mt-6">채널의 이름을 입력해 주세요.
        <input
          className="input mx-auto block mt-2"
          type="text"
          id="channelName"
          placeholder="채널 이름"
          value={channelName}
          onChange={(event: ChangeEvent<HTMLInputElement>) => setChannelName(event.target.value)}
          autoFocus
        />
      </label>
      <label className="block mt-4">채널 입장에 필요한 코드를 입력해 주세요.
        <input
          className="input mx-auto block mt-2"
          type="text"
          id="channelCode"
          placeholder="채널 코드"
          value={channelCode}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            setChannelCode(event.target.value);
            setErrorMsg("");
          }}
        />
      </label>
      <button className="button mt-8" type="button" onClick={fetchPostCreateChannel} disabled={!channelCode || !channelName}>채널 생성</button>
      {errorMsg && <Error errorMessage={errorMsg} />}
    </div>
  );
}

export default CreateChannel;
