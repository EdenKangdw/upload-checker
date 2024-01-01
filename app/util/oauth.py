import httpx

KAKAO_APP_KEY = "635065823fa42e337885faea9b31f3f4"
KAKAO_REDIRECT_URI = "http://localhost:8000/oauth/kakao/redirect"
KAKAO_AUTH_URI = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_URI = "https://kapi.kakao.com/v2/user/me"


def kakao_token(code: str):
    """
    카카오 인증코드를 받아 카카오 인증 api를 호출하고 토큰을 return 한다.
    """

    # send request to KAKAO auth
    with httpx.Client() as client:
        header = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}
        body = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_APP_KEY,
            "redirect_uri": KAKAO_REDIRECT_URI,
            "code": code,
        }
        response = client.post(url=KAKAO_AUTH_URI, headers=header, data=body)
        result = response.json()

    return result


def kakao_login(token):
    """
    카카오 토큰을 받아 유저 정보를 가져옵니다.
    """
    # send request to KAKAO user
    with httpx.Client() as client:
        header = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        response = client.get(url=KAKAO_USER_URI, headers=header)
        result = response.json()
        print("login", result)

    return result
