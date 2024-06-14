from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from config import Config
from database.query import add_user, get_user
from database.schema import User
from util.auth import encode_token
from util.oauth import kakao_login, kakao_token
from database.conn import db

oauth2_scheme = HTTPBearer()
app = APIRouter()

# get config
config = Config()


@app.get("/kakao/redirect", status_code=200)
async def kakao_user_login_api(
    code: str = Query(..., description="카카오 인증코드"),
    session: Session = Depends(db.session),
):
    """
    카카오의 인증코드를 redirect 받아 인증절차를 거친 뒤, token을 return 합니다.
    """
    kakao_access_token = kakao_token(code).get("access_token")
    kakao_user = kakao_login(kakao_access_token)
    nickname = kakao_user["properties"]["nickname"]
    print(nickname)
    # check user9 exist on DB
    if len(session.query(User).filter(User.user_name == nickname).all()) == 0:
        print("User doesn't exists")
        # add user
        user = User(user_name=nickname)
        add_user(session, user)
        print("User added", user.user_name)

        # get user
        user = get_user(session, nickname)
        nickname = user.user_name
        print(nickname)

    # create token
    token = encode_token(nickname)
    CLIENT_REDIRECT_URL = config.CLIENT_REDIRECT_URL

    return RedirectResponse(url=f"{CLIENT_REDIRECT_URL}?access_token={token}")
