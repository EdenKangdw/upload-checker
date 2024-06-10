import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "../../store/auth";
import { useEffect } from "react";
import SpinnerIcon from '../../assets/images/icon/spinner.gif'
import { useUserInfoStore } from "../../store/user";

export default function GetToken () {
  const navigate = useNavigate();
  const [ searchParams ] = useSearchParams();
  const setToken = useAuthStore(state => state.setToken);
  const user_id = useUserInfoStore(state => state.user_id);
  
  useEffect(() => {
    const accessToken = searchParams.get('access_token');
    accessToken && setToken(accessToken)
    user_id ? navigate('/lobby') : navigate('/getUserInfo')
  }, [])

  return (<img src={SpinnerIcon} alt="로딩중" />)
}