from datetime import datetime, timedelta
from typing import Annotated, Union
from fastapi import Body, Depends, FastAPI, Query, Request
from api_model.model import ChannelModel, CheckModel
from database.query import (
    add_channel,
    get_channel,
    get_channel_with_name,
    add_check,
    get_check,
    get_user_checks_channel,
    add_user,
    get_user,
    get_users,
    get_channel_with_code,
    get_channel_checks,
)
from util.auth import get_current_user
from database.conn import engineconn, db
from database.base import Base
from database.schema import User, Channel, Check
from config import Config
from starlette.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from util.oauth import kakao_login, kakao_token
from util.auth import create_access_token, encode_token
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import logging

oauth2_scheme = HTTPBearer()

# template
templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# db connection

engine = engineconn()
session = engine.sessionmaker()
Base.metadata.create_all(bind=engine.engine)

# get config
config = Config()


"""
http://localhost:8000/oauth/kakao/redirect?code=914rIhV3Epl2n9ls6YZL3Kh766OxdsqOe-WQPokOlHqikSB1Neq4URoHYIgKPXRpAAABjMONm8Gxu3fh8M0xkQ
"""


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/user")
async def user_api(
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    # get user info
    user = await get_current_user(token)
    return user


@app.get("/oauth/kakao/redirect", status_code=200)
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
    LOCAL_CLIENT_REDIRECT_URL = "http://localhost:3000/main"
    CLOUD_CLIENT_REDIRECT_URL = (
        "https://web-upload-checker-temp-28f9s2blqx7tnkg.sel5.cloudtype.app/main"
    )
    return RedirectResponse(url=f"{LOCAL_CLIENT_REDIRECT_URL}?access_token={token}")


@app.post("/channel", status_code=200)
async def post_channel_api(
    params: ChannelModel,
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    생성하고자 하는 채널의 정보를 받아 채널을 생성하고, 만들어진 채널의 정보를 return 합니다.
    """
    input = params.dict()

    # check user
    user = await get_current_user(token)

    # create channel
    channel = Channel(
        channel_name=input.get("name"),
        channel_code=input.get("code"),
        channel_creator_id=user.user_id,
        channel_check_type=input.get("check_type"),
    )
    add_channel(session, channel)

    # get channel
    channel_result = await get_channel_with_name(
        session, creator_id=user.user_id, channel_name=channel.channel_name
    )
    return channel_result


@app.post("/check", status_code=200)
async def post_check_api(
    params: CheckModel,
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    출석하고자 하는 채널의 아이디를 받고 출석체크를 한 뒤, 출석 정보를 return 합니다.
    """
    input = params.dict()

    # check user
    user = await get_current_user(token)

    # check
    check = Check(
        check_channel_id=input.get("channel_id"),
        check_user_id=user.user_id,
    )

    add_check(session, check)

    # get check
    check_result = get_check(session, user.user_id, input.get("channel_id"))

    return check_result


@app.get("/check", status_code=200)
async def get_check_api(
    channel_id: int = Query(default=0),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 아이디를 확인하여, 현재 유저가 출석을 했는지 여부를 확인하여 출석 정보를 return 합니다.
    """
    # check user
    user = await get_current_user(token)

    # get current_date check
    current_date_str = datetime.now().strftime("%Y-%m-%d")
    check_result = get_check(
        session,
        channel_id=channel_id,
        user_id=user.user_id,
        created_at=current_date_str,
    )

    return check_result


@app.get("/channel/check", status_code=200)
async def get_check_channel_api(
    channel_id: int = Query(default=0),
    start_date=Query(default="", description="체크기준 시작날짜(KST)"),
    end_date=Query(default="", description="체크기준 종료날짜(KST)"),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널의 생성자가 사용합니다. 채널 내, 일정 기간동안 체크한 사람의 목록을 확인힐 수 있습니다.
    """

    # check user
    user = await get_current_user(token)
    print("user: %s" % user.user_id)

    # check channel creator
    # channel = await get_channel(session, channel_id)
    # print("channel: %s" % channel.channel_creator_id, channel.channel_id)
    # if channel is None:
    #     return None
    # if channel.channel_creator_id != user.user_id:
    #     return "채널의 생성자가 아닙니다"

    # get period

    end_date = start_date if end_date == "" else end_date
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    period_array = [
        start_datetime + timedelta(days=x)
        for x in range((end_datetime - start_datetime).days + 1)
    ]

    # get checks
    channel_check_list = []
    print(period_array)
    for target_datetime in period_array:
        current_date_str = target_datetime.strftime("%Y-%m-%d")
        checks = get_channel_checks(session, channel_id, current_date_str)
        datetime_checks = list(map(lambda x: x.user_name, checks))
        check = {"date": current_date_str, "checks": datetime_checks}
        channel_check_list.append(check)
        print("checks: %s" % datetime_checks)

    return channel_check_list


@app.get("/channel")
async def get_channel_api(
    channel_code=Query(description="채널 코드", default=""),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 코드를 통해 채널 정보를 받은 후, 들어갑니다.
    """
    # user check
    user = await get_current_user(token)

    # get channel with code
    channel = await get_channel_with_code(session, channel_code)

    return dict(channel=channel)


@app.post("/dummy/user", status_code=200)
async def dummy_user(user_name: str, session: Session = Depends(db.session)):
    """
    dummy 유저를 생성합니다.
    """

    # add dummy user
    user = User(user_name=user_name)
    add_user(session, user)

    # get user
    user_result = get_user(session, user_name)

    return user_result


@app.post("/dummy/check", status_code=200)
async def dummy_check(
    channel_id: int = Body(default=0),
    user_id: int = Body(default=0),
    session: Session = Depends(db.session),
):
    """
    dummy로 체크할 수 있는 api 입니다. 채널과 유저 아이디를 받아 체크합니다.
    """

    # dummy check
    check = Check(
        check_channel_id=channel_id,
        check_user_id=user_id,
    )
    add_check(session, check)

    # get check
    today = datetime.now().strftime("%Y-%m-%d")
    check_result = get_check(session, user_id, channel_id, today)

    return check_result


@app.get("/user/list", status_code=200)
async def user_list_api(session: Session = Depends(db.session)):
    return get_users(session)


@app.get("/user/check", status_code=200)
async def user_check(
    session: Session = Depends(db.session),
    token: HTTPBearer = Depends(oauth2_scheme),
    channel_id: int = Query(default=0),
    start_date=Query(default="", description="체크기준 시작날짜(KST)"),
    end_date=Query(default="", description="체크기준 종료날짜(KST)"),
):
    result = []

    # user check
    user = await get_current_user(token)

    print(channel_id, start_date, end_date, user)

    # get user check list
    user_check_list = get_user_checks_channel(
        session, channel_id, user.user_id, start_date, end_date
    )
    checked_date_list = []
    for check in user_check_list:
        checked_date_list.append(check.created_at.strftime("%Y-%m-%d"))

    # get period
    start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    period_array = [
        start_datetime + timedelta(days=x)
        for x in range((end_datetime - start_datetime).days + 1)
    ]

    for target_date in period_array:
        check = {"date": "", "check": "X"}
        if target_date.strftime("%Y-%m-%d") in checked_date_list:
            check["check"] = "O"
        check["date"] = target_date.strftime("%Y-%m-%d")
        result.append(check)

    return result
