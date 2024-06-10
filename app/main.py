from datetime import datetime, timedelta
from typing import Annotated, Optional, Union
from fastapi import Body, Depends, FastAPI, Query, Request
from api_model.model import (
    ChannelModel,
    GroupModel,
    UpdateGroupUserModel,
    UpdateUserModel,
)
from database.query import (
    add_channel,
    add_group,
    add_group_user,
    add_user_channel,
    get_channel,
    get_channel_with_name,
    add_check,
    get_check,
    get_groups,
    get_user_channels,
    get_user_checks_channel,
    add_user,
    get_user,
    get_user_with_id,
    get_users,
    get_channel_with_code,
    get_channel_checks,
    update_group_user,
    update_user_nickname,
)
from util.auth import get_current_user
from database.conn import engineconn, db
from database.base import Base
from database.schema import Group, GroupUser, User, Channel, Check, UserChannel
from config import Config
from starlette.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from util.oauth import kakao_login, kakao_token
from util.auth import create_access_token, encode_token
from fastapi.responses import JSONResponse, RedirectResponse
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
    """
    현재 로그인 되어 있는 유저의 정보를 token 기반하여 return 합니다.
    """
    # get user info
    user = await get_current_user(token)
    return user


@app.post("/user")
async def post_user(
    update_user: UpdateUserModel,
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    유저 정보를 업데이트 합니다. 각각의 정보는 optional 하기 때문에, 1개만 있어도 상관없습니다.
    - nickname : 유저 닉네임
    - group_id : 유저 소속팀 아이디
    """
    # get user info
    user = await get_current_user(token)

    # update user nickname
    if update_user.nickname:
        update_user_result = update_user_nickname(
            session, user.user_id, update_user.nickname
        )
        if not update_user_result:
            return JSONResponse({"error": "fail to update user"}, status_code=500)

    # add user group
    if update_user.group_id:
        group_user = GroupUser(
            user_id=user.user_id,
            group_id=update_user.group_id,
        )
        add_group_user_result = add_group_user(session, group_user)
        if not add_group_user_result:
            return JSONResponse({"error": "fail to add group user"}, status_code=500)

    # get updated user
    updated_user = get_user_with_id(session, user.user_id)
    if not updated_user:
        return JSONResponse({"error": "fail to get user"}, status_code=500)

    return updated_user


@app.post("/group")
async def post_group(
    group: GroupModel,
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    그룹을 생성합니다.
    """
    # get user info
    user = await get_current_user(token)

    # add group
    group = Group(
        group_name=group.name,
    )

    # add group user
    added_group = add_group(session, group)
    if not added_group:
        return JSONResponse({"error": "Could not add group"}, status_code=500)

    return added_group


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
    CLIENT_REDIRECT_URL = config.CLIENT_REDIRECT_URL

    return RedirectResponse(url=f"{CLIENT_REDIRECT_URL}?access_token={token}")


@app.post("/channel", status_code=200, tags=["Channel"])
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
    add_channel_result = add_channel(session, channel)
    if not add_channel_result:
        return JSONResponse({"error": "Can't add channel"}, status_code=500)
    
    # add user channel
    user_channel = UserChannel(
        user_id=user.user_id,
        channel_id=channel.channel_id,
        type="CREATOR",
    )
    add_user_channel(session, user_channel)
    if not add_user_channel:
        return JSONResponse({"error": "Can't add user channel"}, status_code=500)

    # get channel
    channel_result = await get_channel_with_name(
        session, creator_id=user.user_id, channel_name=channel.channel_name
    )
    return channel_result

@app.get('/channel/user', status_code=200, tags=['Channel'])
async def get_channel_user(
    channel_id: int = Query(default=0),
    session: Session = Depends(db.session),
    token: HTTPBearer = Depends(oauth2_scheme),
):
    """
    채널 내 유저 정보를 return 합니다.
    - isManager : 채널 매니저 여부
    - isCreator : 채널 생성자 여부
    """
    # user check
    user = await get_current_user(token)

    # get channel users
    channel_user = get_user_channel_info(session, channel_id, user.user_id)
    if not channel_user:
        return JSONResponse({"error": "Can't get channel user"}, status_code=500)
    
    # set user type option
    result = {
        'user_id': user.user_id,
        'channel_id': channel_id,
        'isManager': False,
        'isCreator': False,
    }
    result['isManager'] = True if channel_user.type in ['MANAGER', 'CREATOR'] else False
    result['isCreator'] = True if channel_user.type == 'CREATOR' else False
    return result

@app.get('/channel/user/type', status_code=200, tags=['Channel'])
async def get_channel_user(
    channel_id: int = Query(default=0),
    session: Session = Depends(db.session),
    token: HTTPBearer = Depends(oauth2_scheme),
):
    """
    선택할 수 있는 채널 내 유저 타입 목록을 return 합니다.
    """
    # user check
    user = await get_current_user(token)

    result = [
        {'type': 'MANAGER', 'name': '관리자'},
        {'type': 'MEMBER', 'name': '멤버'},
    ]
    return result

@app.post('/channel/user', status_code=200, tags=['Channel'])
async def post_channel_user_api(
    channel_id: int = Body(..., description="채널 아이디"),
    user_id: int = Body(..., description="유저 아이디"),
    type: str = Body(..., description="유저 타입(MANAGER, MEMBER)"),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 내 유저 정보를 업데이트 합니다.
    - MEMBER : 일반 유저
    - MANAGER : 매니저
    """
    # user check
    user = await get_current_user(token)
    
    # check is creator
    user_channel = get_user_channel_info(session, channel_id, user.user_id)
    if not user_channel:
        return JSONResponse({"error": "Can't get channel user"}, status_code=500)
    if user_channel.type != 'CREATOR':
        return JSONResponse({"error": "You are not creator"}, status_code=500)
    
    # update group user
    update_group_user_result = update_group_user(
        session, channel_id, user.user_id, type
    )
    if not update_group_user_result:
        return JSONResponse({"error": "can't update group_user"}, status_code=500)

    return True


async def post_check_api(
    channel_id: int = Body(..., description="채널 아이디"),
    checked_at: Optional[str] = Body(description="체크한 target date", default=None),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    출석하고자 하는 채널의 아이디를 받고 출석체크를 한 뒤, 출석 정보를 return 합니다.
    """

    # check user
    user = await get_current_user(token)

    # check date
    checked_at = (
        datetime.strptime(checked_at, "%Y-%m-%d") if checked_at else datetime.now()
    )

    # check
    check = Check(
        check_channel_id=channel_id,
        check_user_id=user.user_id,
        checked_at=checked_at,
    )

    added_check = add_check(session, check)
    if not added_check:
        return JSONResponse({"error": "duplicated check"}, status_code=500)

    # get check
    check_result = get_check(session, user.user_id, channel_id, checked_at)

    return check_result


@app.get("/check", status_code=200)
async def get_check_api(
    channel_id: int = Query(default=0),
    checked_at: str = Query(default=None),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 아이디를 확인하여, 현재 유저가 출석을 했는지 여부를 확인하여 출석 정보를 return 합니다.
    """
    # check user
    user = await get_current_user(token)

    # get current_date check
    # TODO : 체크 이력을 checked_at에서 가져오도록 처리
    checked_at = checked_at if checked_at else datetime.now().strftime("%Y-%m-%d")
    check_result = get_check(
        session, channel_id=channel_id, user_id=user.user_id, checked_at=checked_at
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

    # check group leader

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


@app.post("/channel/join")
async def post_channel_join(
    channel_code=Query(description="채널 코드", default=""),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 코드를 통해 채널 정보를 받은 후, 채널에 가입합니다.
    """
    # user check
    user = await get_current_user(token)

    # get channel with code
    channel = await get_channel_with_code(session, channel_code)
    if not channel:
        return JSONResponse(
            {"error": "채널코드에 해당하는 채널을 찾을 수 없습니다"},
            status_code=500,
        )
    user_channel = UserChannel(user_id=user.user_id, channel_id=channel.channel_id)

    # join channel
    add_user_channel(session, user_channel)

    return dict(channel=channel)


@app.get("/channel")
async def get_channel_api(
    channel_id: int = Query(description="채널 아이디", default=1),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 아이디를 통해 채널 정보를 얻습니다. 채널 입장에 사용합니다.
    """
    # user check
    user = await get_current_user(token)

    # get channel with code
    channel = await get_channel(session, channel_id)

    return dict(channel=channel)


@app.post("/dummy/user", status_code=200)
async def dummy_user(user_name: str, session: Session = Depends(db.session)):
    """
    dummy 유저를 생성한 후 token을 return 합니다.
    """

    # add dummy user
    user = User(user_name=user_name)
    add_user_result = add_user(session, user)
    if not add_user_result:
        return JSONResponse({"error": "Can't add user"}, status_code=500)

    # get user
    user_result = get_user(session, user_name)
    if not user_result:
        return JSONResponse({"error": "User not found"}, status_code=500)

    # TODO : 더미 유저 생성 후, token도 같이 return
    # get dummy user' token
    token = encode_token(user_name)

    return token


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
    today = datetime.now()
    check_result = get_check(session, user_id, channel_id, today)

    return check_result


@app.get("/user/list", status_code=200)
async def user_list_api(session: Session = Depends(db.session)):
    """
    서버에 존재하는 유저 정보를 모두 return 합니다.
    """
    return get_users(session)


@app.get("/user/check", status_code=200)
async def user_check(
    session: Session = Depends(db.session),
    token: HTTPBearer = Depends(oauth2_scheme),
    channel_id: int = Query(default=0),
    start_date=Query(default="", description="체크기준 시작날짜(KST)"),
    end_date=Query(default="", description="체크기준 종료날짜(KST)"),
):
    """
    로그인 한 유저가 특정 채널에 대해 출석한 기록을 return 합니다.
    """
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


@app.get("/user/channel", status_code=200)
async def get_user_channel(
    session: Session = Depends(db.session), token: HTTPBearer = Depends(oauth2_scheme)
):
    """
    유저가 가입한 채널 목록을 return 합니다
    """
    # user check
    user = await get_current_user(token)

    # get user's channels
    user_channels = get_user_channels(session, user.user_id)

    return user_channels


@app.get("/group/list", status_code=200)
async def get_group_list(
    session: Session = Depends(db.session), token: HTTPBearer = Depends(oauth2_scheme)
):
    """
    전체 팀 목록을 return 합니다.
    """
    # user check
    user = await get_current_user(token)

    # get group list
    group_list = get_groups(session)
    if not group_list:
        return JSONResponse({"error": "cannot get groups"}, status_code=500)

    return group_list


@app.post("/group/user")
async def post_group_user(
    group_user: UpdateGroupUserModel,
    session: Session = Depends(db.session),
    token: HTTPBearer = Depends(oauth2_scheme),
):
    """
    팀 내에서 유저 정보를 업데이트 합니다.
    - type : LEADER, MEMBER
    """
    # user check
    user = await get_current_user(token)

    # update group user
    update_group_user_result = update_group_user(
        session, group_user.group_id, user.user_id, group_user.type
    )
    if not update_group_user_result:
        return JSONResponse({"error": "can't update group_user"}, status_code=500)

    return True
