import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
// import DatePicker from 'react-datepicker';
// import 'react-datepicker/dist/react-datepicker.css';
import instance from "../../api/axiosConfig";
import { useChannelInfoStore } from "../../store/channel";
import { getMyCheckList, getCheckPeriodList } from "../../types/channel";
import CalendarIcon from '../assets/images/icon/ico-calendar.svg';
import HomeIcon from  '../../assets/images/icon/ico-home.svg'
import classNames from "classnames";

export default function ChannelRoom() {
  const location = useLocation();
  const navigate = useNavigate();
  const {channel_id, channel_name } = useChannelInfoStore(state => ({
    channel_id: state.channel_id,
    channel_name: state.channel_name
  }));

  const [checked, setChecked] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<"DAY" | "PERIOD" | "MY_ATTENDANCE">("DAY");


  const [totalCheckList, setTotalCheckList] = useState<getCheckPeriodList[]>([]); // 기간 조회
  const [todayCheckList, setTodayCheckList] = useState<getCheckPeriodList[]>([]); // 하루 조회
  const [myCheckList, setMyCheckList] = useState<getMyCheckList[]>([]); // 나의 출석 조회
  const [startDate, setStartDate] = useState<Date | null>(new Date());
  const [endDate, setEndDate] = useState<Date | null>(new Date());
  const [summarySwitch, setSummarySwitch] = useState(true);



  const postAttendanceCheck = async () => {
    try {
      await instance.post("/check", {
        channel_id: channel_id,
      }).then(res => {
        console.log("서버 응답:", res);
        setChecked(true);
      })
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  const getTodayCheckList = async () => {
    try {
      setEndDate(null);
      await instance.get(`/channel/check`, {
        params: {
          channel_id: channel_id,
          start_date: startDate && startDate.toISOString().split("T")[0],
          end_date: "",
        },
      }).then(res => {
        setTotalCheckList([]);
        setMyCheckList([]);
        setTodayCheckList(res.data);
      })
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  const getTotalCheckList = async () => {
    try {
      if (!(startDate && endDate)) {
        alert("기간 조회를 위해 시작일과 종료일을 지정해주세요.");
        return false;
      }

      if (startDate > endDate) {
        alert("시작일이 종료일보다 뒤에 있습니다.");
        return false;
      }

      // 체크 리스트 요청을 보냄
      const response = await instance.get("/channel/check", {
        params: {
          channel_id: channel_id,
          start_date: startDate.toISOString().split("T")[0],
          end_date: endDate !== null ? endDate.toISOString().split("T")[0] : "",
        },
      });
      console.log("서버 응답:", response.data);
      setTodayCheckList([]);
      setMyCheckList([]);
      setTotalCheckList(response.data);
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  const getMyCheckList = async () => {
    try {
      // 체크 리스트 요청을 보냄

      if (!(startDate && endDate)) {
        alert("나의 출석체크 조회를 위해 시작일과 종료일을 지정해주세요.");
        return false;
      }

      if (startDate > endDate) {
        alert("시작일이 종료일보다 뒤에 있습니다.");
        return false;
      }

      const response = await instance.get("/user/check", {
        params: {
          channel_id: channel_id,
          start_date: startDate.toISOString().split("T")[0],
          end_date: endDate !== null ? endDate.toISOString().split("T")[0] : "",
        },
      });

      console.log("서버 응답:", response.data);
      setTodayCheckList([]);
      setTotalCheckList([]);
      setMyCheckList(response.data);
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };

  useEffect(() => {
    getTodayCheckList();
  }, [])

  console.log('activeTab',activeTab)

  return (
    <div className="wrapper gap-5">
      <button className="w-8" type="button" onClick={() => navigate("/lobby")}>
        <img src={HomeIcon} alt="홈으로 가기" />
      </button>

      <p className="title">{channel_name}</p>
   
      <div className="flex justify-between items-center">
        <p>출석체크 여부 : {checked && "O"}</p>
        <button className="button" type="button" onClick={postAttendanceCheck}>출석체크</button>
      </div>

      {/* <div>
        <label className="relative inline-block">시작일 : 
          <DatePicker
            className="bg-primary cursor-pointer border-b outline-none"
            dateFormat='yyyy.MM.dd' 
            shouldCloseOnSelect 
            selected={startDate}
            onChange={(date) => setStartDate(date)}
            locale="ko"
            showIcon
          />
        </label>

        <label className="relative inline-block">종료일 : 
          <DatePicker 
            className="bg-primary cursor-pointer border-b outline-none"
            dateFormat='yyyy.MM.dd' 
            shouldCloseOnSelect 
            selected={endDate} 
            onChange={(date) => setEndDate(date)} 
          />
       </label>
      </div> */}
      
      {/* <div className="flex justify-between items-center gap-2">
        <button
          className={classNames("tab", {" bg-primary-1": activeTab === "DAY"} )}
          type="button" 
          onClick={() => {
            setActiveTab("DAY");
            getTodayCheckList();
          }}
        >
          하루 조회
        </button>
        <button 
          className={classNames("tab", {"bg-primary-1": activeTab === "PERIOD"} )}
          type="button" 
          onClick={() => {
            setActiveTab("PERIOD"); 
            getTotalCheckList();
            }}
          >
            기간 조회
        </button>
        <button 
          className={classNames("tab", {"bg-primary-1": activeTab === "MY_ATTENDANCE"} )}
          type="button" 
          onClick={() => {
            setActiveTab("MY_ATTENDANCE"); 
            getMyCheckList();
            }}
          >
            나의 출석 조회
        </button>
      </div>
      */}
    
{/* 
      {totalCheckList.length > 0 && (
        <table className="tableWithBorder">
          <thead>
            <tr>
              <th>날짜</th>
              <th>출석 수</th>
              <th>출석자</th>
            </tr>
          </thead>
          <tbody>
            {totalCheckList.map((entry, index) => (
              <tr key={index} onClick={() => setSummarySwitch(!summarySwitch)}>
                <td>{entry.date}</td>
                <td>{entry.checks.length}</td>
                <td>
                  {summarySwitch ? (
                    <ul
                      style={{ listStyleType: "none", paddingInlineStart: "0" }}
                    >
                      {entry.checks.length > 0 ? (
                        <li key={index}>
                          {entry.checks.length > 1
                            ? `${entry.checks[0]} 외 ${
                                entry.checks.length - 1
                              } 명`
                            : entry.checks[0]}
                        </li>
                      ) : (
                        <li key={index}>-</li>
                      )}
                    </ul>
                  ) : (
                    <ul
                      style={{ listStyleType: "none", paddingInlineStart: "0" }}
                    >
                      {entry.checks.map((user, userIndex) => (
                        <li key={userIndex}>{user}</li>
                      ))}
                    </ul>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {todayCheckList.length > 0 && (
        <table className="tableWithBorder">
          <thead>
            <tr>
              <th>날짜</th>
              <th>출석 수</th>
              <th>출석한 사용자</th>
            </tr>
          </thead>
          <tbody>
            {todayCheckList.map((entry, index) => (
              <tr key={index}>
                <td>{entry.date}</td>
                <td>{entry.checks.length}</td>
                <td>
                  <ul
                    style={{ listStyleType: "none", paddingInlineStart: "0" }}
                  >
                    {entry.checks?.map((user, userIndex) => (
                      <li key={userIndex}>{user}</li>
                    ))}
                  </ul>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {myCheckList.length > 0 && (
        <table className="tableWithBorder">
          <thead>
            <tr>
              <th>날짜</th>
              <th>나의 출석 여부</th>
            </tr>
          </thead>
          <tbody>
            {myCheckList.map((entry, index) => (
              <tr key={index}>
                <td>{entry.date}</td>
                <td>{entry.check}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )} */}
    </div>
  );
}

