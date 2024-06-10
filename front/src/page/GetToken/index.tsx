import { useNavigate, useSearchParams } from "react-router-dom";
import { useAuthStore } from "../../store/auth";
import { useEffect } from "react";
import SpinnerIcon from '../../assets/images/icon/spinner.gif'

export default function GetToken () {
  const navigate = useNavigate();
  const [ searchParams ] = useSearchParams();
  const { setToken } = useAuthStore();
  
  useEffect(() => {
    const accessToken = searchParams.get('access_token');
    accessToken && setToken(accessToken)
    navigate('/getUserInfo')
  }, [])

  return (<img src={SpinnerIcon} alt="로딩중" />)
}