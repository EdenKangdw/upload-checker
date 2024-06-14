from datetime import datetime, time, timedelta
from typing import Optional
from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
from api_model.model import ChannelModel
from sqlalchemy.orm import Session
from database.query import add_check, get_check, get_period_check
from database.schema import Check
from util.auth import get_current_user
from database.conn import db

oauth2_scheme = HTTPBearer()
app = APIRouter()


@app.post("/", status_code=200)
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


@app.post("/late", status_code=200)
async def post_check_late_api(
    channel_id: int = Body(..., description="채널 아이디"),
    checked_at: str = Body(description="체크한 target date", default=None),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    [ 늦게체크 API ]

    출석하고자 하는 채널의 아이디를 받고 출석체크를 한 뒤, 출석 정보를 return 합니다.
    - 체크 날짜를 받고 시간은 채널의 기준시간으로 맞추어 적용합니다.
    """

    # check user
    user = await get_current_user(token)

    STANDARD_CHECK_TIME = 18

    # check date
    checked_at = datetime.combine(
        datetime.strptime(checked_at, "%Y-%m-%d"), time(STANDARD_CHECK_TIME, 10)
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


@app.get("/", status_code=200)
async def get_check_api(
    channel_id: int = Query(default=0),
    checked_at: str = Query(default=None),
    token: HTTPBearer = Depends(oauth2_scheme),
    session: Session = Depends(db.session),
):
    """
    채널 아이디를 확인하여, 현재 유저가 출석을 했는지 여부를 확인하여 출석 정보를 return 합니다.
    - 당일 기준시간 이전의 체크가 존재하면, check 이력을 return 하고
    - 당일 기준시간 이전의 체크가 존재하지 않으면, None을 return 합니다.
    - 토요일이면 기준 시간은 오후 12시가 됨
    """
    # check user
    user = await get_current_user(token)

    checked_at = (
        datetime.strptime(checked_at, "%Y-%m-%d") if checked_at else datetime.now()
    )

    SATURDAY_CHECK_TIME = 12
    # check saturday
    print(checked_at)
    if checked_at.weekday() == 5:
        # 토요일 체크
        check_start_time = datetime.combine(
            checked_at.date(), time(SATURDAY_CHECK_TIME, 0)
        )
        check_end_time = datetime.combine(checked_at.date(), time(23, 59, 59))
        print(check_end_time, check_start_time)
    else:
        # 평일 체크
        STANDARD_CHECK_TIME = 18
        if datetime.now().time().hour < STANDARD_CHECK_TIME:
            check_end_time = datetime.combine(
                checked_at.date(), time(STANDARD_CHECK_TIME, 0)
            )
            check_start_time = check_end_time - timedelta(days=1)
        else:
            check_start_time = datetime.combine(
                checked_at.date(), time(STANDARD_CHECK_TIME, 0)
            )
            check_end_time = check_start_time + timedelta(days=1)

    # get current_date check
    check_result = get_period_check(
        session,
        channel_id=channel_id,
        user_id=user.user_id,
        check_start_time=check_start_time,
        check_end_time=check_end_time,
    )

    return check_result
