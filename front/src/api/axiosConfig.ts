import axios from 'axios';
import { useAuthStore } from '../store/auth';

export const BASE_URL = process.env.REACT_APP_API_BASE_URL;
const instance = axios.create({
  baseURL: BASE_URL,
});

// withCredentials 전역 설정 - CORS cookies 전송
instance.defaults.withCredentials = false;

// 요청 인터셉터 추가하기
instance.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    config.headers['Content-Type'] = 'application/json';
    config.headers['Authorization'] = `Bearer ${token}`;

    return config;
  },
  (error) => {
    return Promise.reject(error);
  },
);

// 응답 인터셉터 추가하기
instance.interceptors.response.use(
  (response) => {

    // 2xx 범위에 있는 상태 코드는 이 함수를 트리거 합니다.
    // 응답 데이터가 있는 작업 수행
    if (response.status === 404) {
      console.log('404 페이지로 넘어가야 함!');
    }

    return response;
  },
  async (error) => {

    // 2xx 외의 범위에 있는 상태 코드는 이 함수를 트리거 합니다.
    // 응답 오류가 있는 작업 수행
    // if (error.response?.status === 401) {
    //   // isTokenExpired() - 토큰 만료 여부를 확인하는 함수
    //   // tokenRefresh() - 토큰을 갱신해주는 함수
    //   if (isTokenExpired()) await tokenRefresh();

    //   const accessToken = getToken();

    //   error.config.headers = {
    //     'Content-Type': 'application/json',
    //     Authorization: `Bearer ${accessToken}`,
    //   };

    //   // 중단된 요청을(에러난 요청)을 토큰 갱신 후 재요청
    //   const response = await axios.request(error.config);
    //   return response;
    // }
    return Promise.reject(error);
  }
);

export default instance;
