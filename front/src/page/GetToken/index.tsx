import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "../../store/auth";
import { useEffect } from "react";
import SpinnerIcon from '../../assets/images/icon/spinner.gif'
import instance from "../../api/axiosConfig";

export default function GetToken () {
  const navigate = useNavigate();
  const [ searchParams ] = useSearchParams();
  const setToken = useAuthStore(state => state.setToken);

  const fetchGetUserInfo = async () => {
    try {
      await instance.get("/user").then(res => {
        Object.keys(res.data).includes('groups') ? navigate('/lobby') : navigate('/getUserInfo');
      })
    } catch (error) {
      console.error("오류 발생:", error);
    }
  };
  
  useEffect(() => {
    const accessToken = searchParams.get('access_token');
    accessToken && setToken(accessToken);
    fetchGetUserInfo();
  }, [])

  return (<img src={SpinnerIcon} alt="로딩중" />)
}