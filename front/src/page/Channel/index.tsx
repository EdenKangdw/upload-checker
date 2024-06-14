import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import instance from "../../api/axiosConfig";
import { getMyCheckList } from "../../types/channel";
import HomeIcon from  '../../assets/images/icon/ico-home.svg'
import DatePicker, { registerLocale } from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { ko } from 'date-fns/locale';
import dayjs from "dayjs";
registerLocale('ko', ko);

export default function ChannelRoom() {
  const location = useLocation();
  const { data }= location.state || {};
  const navigate = useNavigate();

  const [checked, setChecked] = useState<boolean>(false);
  // const [activeTab, setActiveTab] = useState<"DAY" | "PERIOD" | "MY_ATTENDANCE">("DAY");
  // const [totalCheckList, setTotalCheckList] = useState<getCheckPeriodList[]>([]); // 기간 조회
  // const [todayCheckList, setTodayCheckList] = useState<getCheckPeriodList[]>([]); // 하루 조회
  const [myCheckList, setMyCheckList] = useState<getMyCheckList[]>([]); // 나의 출석 조회
  // const [startDate, setStartDate] = useState<Date | null>(new Date());
  // const [endDate, setEndDate] = useState<Date | null>(new Date());
  // const [checkedAt, setCheckedAt] = useState<Date | null>(null);
  // const [summarySwitch, setSummarySwitch] = useState(true);

  const [dateRange, setDateRange] = useState([new Date(), null]);
  const [startDate, endDate] = dateRange;

  const fetchPostAttendanceCheck = async () => {
    try {
      await instance.post("/check", {
        channel_id: data.channel.channel_id,
      }).then(res => {
        console.log("서버 응답:", res);
        fetchGetAttendanceCheck();
      });
    } catch (error) {
      console.error("오류 발생:", error);
    };
  };

  // const getTodayCheckList = async () => {
  //   try {
  //     setEndDate(null);
  //     await instance.get(`/channel/check`, {
  //       params: {
  //         channel_id: channel_id,
  //         start_date: startDate && startDate.toISOString().split("T")[0],
  //         end_date: "",
  //       },
  //     }).then(res => {
  //       setTotalCheckList([]);
  //       setMyCheckList([]);
  //       setTodayCheckList(res.data);
  //     })
  //   } catch (error) {
  //     console.error("오류 발생:", error);
  //   }
  // };

  // const getTotalCheckList = async () => {
  //   try {
  //     if (!(startDate && endDate)) {
  //       alert("기간 조회를 위해 시작일과 종료일을 지정해주세요.");
  //       return false;
  //     }

  //     if (startDate > endDate) {
  //       alert("시작일이 종료일보다 뒤에 있습니다.");
  //       return false;
  //     }

  //     // 체크 리스트 요청을 보냄
  //     const response = await instance.get("/channel/check", {
  //       params: {
  //         channel_id: channel_id,
  //         start_date: startDate.toISOString().split("T")[0],
  //         end_date: endDate !== null ? endDate.toISOString().split("T")[0] : "",
  //       },
  //     });
  //     console.log("서버 응답:", response.data);
  //     setTodayCheckList([]);
  //     setMyCheckList([]);
  //     setTotalCheckList(response.data);
  //   } catch (error) {
  //     console.error("오류 발생:", error);
  //   }
  // };

  // 본인 출석체크 기간 조회
  const fetchGetMyCheckList = async () => {
    try {
      if (!(startDate && endDate)) return alert("시작일과 종료일을 지정해주세요.");
      if (startDate > endDate) return alert("시작일이 종료일보다 뒤에 있습니다.");

      await instance.get(
        `/user/check?channel_id=${data.channel.channel_id}&start_date=${dayjs(startDate).format('YYYY-MM-DD')}&end_date=${dayjs(endDate).format('YYYY-MM-DD')}`
      ).then(res => {
        console.log("서버 응답:", res.data);
        setMyCheckList(res.data);
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

  useEffect(() => {
    fetchGetAttendanceCheck();
  }, []);


  return (
    <div className="wrapper gap-5">
      <button className="w-8" type="button" onClick={() => navigate("/lobby")}>
        <img src={HomeIcon} alt="홈으로 가기" />
      </button>

      <p className="title">{data.channel.channel_name}</p>

      <div className="flex justify-between items-center">
        <p>출석체크 여부 : {checked ? "O": "X"}</p>
        <button className="button" type="button" onClick={fetchPostAttendanceCheck} disabled={checked}>출석체크</button>
      </div>

      <div className="w-full">
        <p>나의 출석 현황 조회</p>
        <div className="flex justify-between items-center gap-2 mt-2">
          <div className="flex-auto">
            <DatePicker
              className="w-full px-2 py-1 rounded-md"
              selectsRange={true}
              startDate={startDate}
              endDate={endDate}
              onChange={(update) => setDateRange(update)}
              withPortal
              locale={ko}
              dateFormat="yyyy/MM/dd"
              placeholderText="시작일 - 종료일"
              isClearable // 입력값 지우는 clear 버튼
              maxDate={new Date()}
            />
          </div>
          <button className="button flex-none" type="button" onClick={fetchGetMyCheckList}>
            조회
          </button>
        </div>
      </div>

      {/* <div>
        <p className="mb-4">이전 날짜 지정해서 체크하기</p>
        <label className="relative inline-block">시작일 : 
          <DatePicker
            className="bg-transparent cursor-pointer border-b-2 border-button outline-none"
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
            className="bg-transparent cursor-pointer border-b-2 border-button outline-none"
            dateFormat='yyyy.MM.dd' 
            shouldCloseOnSelect 
            selected={endDate} 
            onChange={(date) => setEndDate(date)} 
            locale="ko"
            showIcon
          />
      </label>
      <button type="button" onClick={() => {}}>조회</button>
      </div> */}


{/* 
      <label className="relative inline-block">이전 날짜 지정해서 체크하기
          <DatePicker
            className="bg-transparent cursor-pointer border-b-2 border-button outline-none"
            dateFormat='yyyy.MM.dd' 
            shouldCloseOnSelect 
            selected={checkedAt}
            onChange={(date) => setCheckedAt(date)}
            locale={ko}
            showIcon
          />
        </label> */}


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
      
     <div className="flex justify-between items-center gap-2">
        {/* <button
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
        </button> */}
        
      </div>
     
    

      {/* {totalCheckList.length > 0 && (
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
      )} */}
    
      {myCheckList.length > 0 && (
        <table>
          <thead>
            <tr className="tr border-b border-solid border-[#B9D7EA]">
              <th>날짜</th>
              <th>나의 출석 여부</th>
              <th>변경</th>
            </tr>
          </thead>
          <tbody>
            {myCheckList.map((item, idx) => (
              <tr key={idx} className="tr">
                <td>{item.date}</td>
                <td>{item.check}</td>
                <td>
                  <button type="button" className="button1" onClick={() => fetchPostCheckLateDate(item.date)}>
                    출석체크
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )} 
    </div>
  );
}

