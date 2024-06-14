from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from api_model.model import ChannelModel, UpdateUserModel
from sqlalchemy.orm import Session
from database.query import (
    add_group_user,
    get_group_users,
    get_user_channels,
    get_user_checks_channel,
    get_user_with_id,
    get_users,
    update_user_nickname,
)
from database.schema import GroupUser
from util.auth import get_current_user
from database.conn import db

oauth2_scheme = HTTPBearer()
app = APIRouter()


@app.get("/")
async def user_api(
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    현재 로그인 되어 있는 유저의 정보를 token 기반하여 return 합니다.
    """
    # get user info
    user = await get_current_user(token)

    # get user group_info
    group_users = get_group_users(session, user.user_id)
    result = user.__dict__
    if group_users:
        result["groups"] = group_users

    return result


@app.post("/")
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


@app.get("/list", status_code=200)
async def user_list_api(session: Session = Depends(db.session)):
    """
    서버에 존재하는 유저 정보를 모두 return 합니다.
    """
    return get_users(session)


@app.get("/check", status_code=200)
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
        checked_date_list.append(check.checked_at.strftime("%Y-%m-%d"))

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


@app.get("/channel", status_code=200)
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
