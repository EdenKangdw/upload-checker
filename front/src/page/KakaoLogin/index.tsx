export default function KakaoLogin() {
  const KAKAO_REST_API_KEY = process.env.REACT_APP_KAKAO_REST_API_KEY;
  const REDIRECT_URI = `${process.env.REACT_APP_API_BASE_URL}/oauth/kakao/redirect`;

  // oauth 요청 URL
  const kakaoUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${KAKAO_REST_API_KEY}&redirect_uri=${REDIRECT_URI}&response_type=code`;

  return (
    <div className="wrapper justify-center">
      <em className="mb-9 text-lg font-bold">
        너는 내게 부르짖으라
        <br />내가 네게 응답하겠고
        <br />네가 알지 못하는 크고 은밀한 일을
        <br />네게 보이리라  
        <br />
        <br />-렘33:3-
      </em> 
      <button type="button" className="self-end" onClick={() => (window.location.href = kakaoUrl)}>
        <img
          src="https://k.kakaocdn.net/14/dn/btroDszwNrM/I6efHub1SN5KCJqLm1Ovx1/o.jpg"
          alt="카카오 로그인 버튼"
        />
      </button>
    </div>
  );
}
