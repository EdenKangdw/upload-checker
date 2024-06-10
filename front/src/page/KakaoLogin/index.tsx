export default function KakaoLogin() {
  const KAKAO_REST_API_KEY = process.env.REACT_APP_KAKAO_REST_API_KEY;
  const REDIRECT_URI = `${process.env.REACT_APP_API_BASE_URL}/oauth/kakao/redirect`;

  // oauth 요청 URL
  const kakaoUrl = `https://kauth.kakao.com/oauth/authorize?client_id=${KAKAO_REST_API_KEY}&redirect_uri=${REDIRECT_URI}&response_type=code`;

  return (
    <div className="wrapper justify-center">
      <em className="mb-9 text-5xl font-bold">
        In love with
        <br /> each other
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
