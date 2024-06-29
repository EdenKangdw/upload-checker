import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import instance from "../../api/axiosConfig";
import { getCheckPeriodList, getMyCheckList } from "../../types/channel";
import HomeIcon from  '../../assets/images/icon/ico-home.svg'
import CloseIcon from  '../../assets/images/icon/ico-close.svg'
import DatePicker, { registerLocale } from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { ko } from 'date-fns/locale';
import dayjs from "dayjs";
import classnames from "classnames";
import { useChannelUserInfoStore } from "../../store/channelUser";
registerLocale('ko', ko);

export default function ChannelRoom() {
  const location = useLocation();
  const { data }= location.state || {};
  const navigate = useNavigate();
  const isManager = useChannelUserInfoStore(state => state.isManager);

  const [openChecksModal, setOpenChecksModal] = useState<{open: boolean; date: string, checks: string[]}>({open: false, date: "", checks: []});
  const [checked, setChecked] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"PERIOD" | "MY_ATTENDANCE">("MY_ATTENDANCE");
  const isMyAttendance = activeTab === "MY_ATTENDANCE";
  const [myCheckList, setMyCheckList] = useState<getMyCheckList[]>([]); // 나의 출석 조회
  const [channelUserCheckList, setChannelUserCheckList] = useState<getCheckPeriodList[]>([]); // 채널유너들 출석 조회
  const [myDateRange, setMyDateRange] = useState<[Date | null, Date | null]>([null, null]);
  const [myStartDate, myEndDate] = myDateRange;
  const [periodDateRange, setPeriodDateRange] = useState<[Date | null, Date | null]>([null, null]);
  const [periodStartDate, periodEndDate] = periodDateRange;

  const fetchPostAttendanceCheck = async () => {
    try {
      await instance.post("/check", {
        channel_id: data.channel.channel_id,
      }).then(res => {
        if(res.data === null) return alert("지금은 체크 시간이 아닙니다. 평일(18:00-23:59), 토요일(12:00-23:59)에 다시 시도해 주세요.")
        fetchGetAttendanceCheck();
      });
    } catch (error) {
      console.error("오류 발생:", error);
    };
  };

  // 본인 출석체크 기간 조회
  const fetchGetMyCheckList = async () => {
    try {
      if (!(myStartDate && myEndDate)) return alert("시작일과 종료일을 지정해주세요.");
      if (myStartDate > myEndDate) return alert("시작일이 종료일보다 뒤에 있습니다.");

      await instance.get(
        `/user/check?channel_id=${data.channel.channel_id}&start_date=${dayjs(myStartDate).format('YYYY-MM-DD')}&end_date=${dayjs(myEndDate).format('YYYY-MM-DD')}`
      ).then(res => {
        // console.log("서버 응답:", res.data);
        setMyCheckList(res.data);
      });
    } catch (error) {
      console.error("오류 발생:", error);
    };
  };

  // 기간 채널 유저들 출석 조회 
  const fetchGetChannelUserCheckList = async () => {
    try {
      if(!(periodStartDate && periodEndDate)) return alert("시작일과 종료일을 지정해주세요.");
      if(periodStartDate > periodEndDate) return alert("시작일이 종료일보다 뒤에 있습니다.");

      await instance.get(
        `/channel/check?channel_id=${data.channel.channel_id}&start_date=${dayjs(periodStartDate).format('YYYY-MM-DD')}&end_date=${dayjs(periodEndDate).format('YYYY-MM-DD')}`
      ).then(res => {
        setChannelUserCheckList(res.data);
      });
    } catch (error) {
      console.error("오류 발생:", error);
    };
  };

  // 지난 날짜 출석 체크
  const fetchPostCheckLateDate = async (lateDate: string) => {
    try {
      await instance.post("/check/late", {
        channel_id: data.channel.channel_id,
        checked_at: lateDate,
      }).then(res => {
        console.log("서버 응답:", res.data);
        fetchGetMyCheckList();
      });
    } catch (error) {
      console.error("오류 발생:", error);
    };
  };

  // 본인 출석체크한 결과값 보기
  const fetchGetAttendanceCheck = async () => {
    try {
      await instance.get(`/check?channel_id=${data.channel.channel_id}&checked_at=${dayjs().format('YYYY-MM-DD')}`).then(res => {
        res.data?.checked_at? setChecked(true) : setChecked(false);
      });
    } catch (error) {
      console.error("오류 발생:", error);
    };
  };

  // 하루 전날
  const handleGetYesterday = () => {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(today.getDate() - 1);
    return yesterday;
  };

  const handleCheckAttendance = () => {
    const checkHandler = {
      PERIOD: fetchGetChannelUserCheckList,
      MY_ATTENDANCE: fetchGetMyCheckList,
    };
    return checkHandler[activeTab]();
  };

  useEffect(() => {
    fetchGetAttendanceCheck();
  }, []);

  return (
    <div className="wrapper gap-5">
      <button className="w-8" type="button" onClick={() => navigate("/lobby")}>
        <img src={HomeIcon} alt="홈으로 가기" />
      </button>

      <p className="title">{data.channel.channel_name}</p>

      <div>
        <div className="flex flex-wrap justify-between items-center">
          <p>출석체크 여부 : {checked ? "O": "X"}</p>
          <button className="button" type="button" onClick={fetchPostAttendanceCheck} disabled={checked}>출석체크</button>
        </div>
        <p className="text-[#D72323]">* 평일(18:00-23:59), 토요일(12:00-23:59)에 체크 가능합니다.</p>
      </div>

      <div>
        <button 
          type="button" 
          className={classnames("w-6/12 px-2 py-0.5 border border-button-2", {"bg-button-2": isMyAttendance})} 
          onClick={() => setActiveTab("MY_ATTENDANCE")}
        >
          나의 출석 조회
        </button>
        {isManager && <button 
          type="button" 
          className={classnames("w-6/12 px-2 py-0.5 border border-button-2", {"bg-button-2": !isMyAttendance})} 
          onClick={() => setActiveTab("PERIOD")}
        >
          기간 인원 조회
        </button>}
      </div>

      <div className="flex justify-between items-center gap-2 mt-2">
        <div className="flex-auto">
          <DatePicker
            className="w-full px-2 py-1 rounded-md"
            selectsRange={true}
            startDate={isMyAttendance ? myStartDate : periodStartDate}
            endDate={isMyAttendance ? myEndDate : periodEndDate}
            onChange={(update) => isMyAttendance ? setMyDateRange(update) : setPeriodDateRange(update)}
            withPortal
            locale={ko}
            dateFormat="yyyy/MM/dd"
            placeholderText="시작일 - 종료일"
            isClearable // 입력값 지우는 clear 버튼
            maxDate={new Date()}
          />
        </div>
        <button className="button flex-none" type="button" onClick={handleCheckAttendance}>
          조회
        </button>
      </div>

      {isMyAttendance && myCheckList.length > 0 && (
        <table>
          <thead>
            <tr className="tr border-b border-solid border-[#B9D7EA]">
              <th>날짜</th>
              <th>출석 여부</th>
              <th>출석체크 변경</th>
            </tr>
          </thead>
          <tbody>
            {myCheckList.map((item, idx) => (
              <tr key={idx} className="tr">
                <td>{item.date}({item.week_day})</td>
                <td>{item.check}</td>
                <td>
                  <button type="button" className="button1" onClick={() => fetchPostCheckLateDate(item.date)}>
                    변경
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      
      {!isMyAttendance && channelUserCheckList.length > 0 && (
        <div className="h-80">
          <table className="w-full">
            <thead>
              <tr className="tr border-b border-solid border-[#B9D7EA]">
                <th>날짜</th>
                <th>출석 수</th>
                <th>출석자</th>
              </tr>
            </thead>
            <tbody>
              {channelUserCheckList.map((item, idx) => (
                <tr key={idx} className="tr">
                  <td>{item.date}</td>
                  <td>{item.checks.length}명</td>
                  <td>
                    <button 
                      type="button"
                      className="button"
                      onClick={() => setOpenChecksModal({open: true, date: item.date, checks: item.checks})} 
                      disabled={Boolean(!item.checks.length)}
                    >
                        출석자 보기
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )} 

      {openChecksModal.open && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="relative bg-white rounded-lg shadow-lg px-6 pt-12 pb-6 max-w-lg w-full">
            <p>{openChecksModal.date.slice(5)} {openChecksModal.checks.length}명</p>
            <div>{openChecksModal.checks.map(check => <span>{check}, </span>)}</div>
            <button 
              type="button"
              className="absolute top-2 right-2 w-8"
              onClick={() => setOpenChecksModal({open: false, date:"", checks: []})}
            >
              <img src={CloseIcon} alt="닫기" />
            </button>
            <button
              type="button"
              className="button1 absolute top-2 right-12"
              onClick={() => navigator.clipboard.writeText(openChecksModal.checks.join())}
            >
              클립보드
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

